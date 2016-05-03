#!/usr/bin/python3

import os
import subprocess
import sys
import time


CHANGE_LOG = """
2.1
===
- improved logging
- saving information about what changes are being made to files
2.2
===
- cli arguments parsing
- change log
- name was changed from backup_script_for_my_drives_(version).py to \
backup_my_drives.py
2.3
===
- print smartctl errors
- save to log file the list of all dirs selected
- save to log file exact rsync commands used
3.0
===
- moved to python 3
- using rsnapshot rather than rsync to save disk space and have full history
- using rsnapshot logging
- sticking with one approach (fully functional rather than func + oop)
- pep8 compliant
"""

VERSION = """
3.0
"""

START_TIME = time.strftime('%Y%m%d-%H:%M:%S')
SMARTCTL_METRICS = ['5', '187', '188', '196', '197', '198']

# ==========================================================================
#                   library
# ==========================================================================


def get_input(msg):
    try:
        user_input = input(msg)
    except (KeyboardInterrupt, EOFError):
        print('Bye.')
        sys.exit(0)
    return user_input


def confirm_quit(msg):
    choice = get_input(msg)
    if choice != 'y':
        print('Bye.')
        sys.exit(0)
    else:
        pass


def mkdir(path):

    try:
        # check if dir exists
        if not os.path.exists(path):
            # try to create the directory
            res = subprocess.check_call(['mkdir', path])
            # failed to create dir if return code is different than zero
            if res:
                print('Failed to create ' + path)
            else:
                print(path + ' created.')
        else:
            print(path + ' already exists! skipping...')
    except subprocess.CalledProcessError:
        print('subprocess error')
        pass
    except OSError as err:
        print(err)
        sys.exit(1)


def clr_scr():
    subprocess.check_call(
        '/usr/bin/clear',
        shell=True
    )

# ==========================================================================
#                   script
# ==========================================================================


def run():
    print('Starting backup...')

    subprocess.check_call(
        '/usr/local/bin/rsnapshot -c ./rsnapshot.conf configtest',
        shell=True
    )

    subprocess.check_call(
        '/usr/local/bin/rsnapshot -c ./rsnapshot.conf alpha',
        shell=True
    )

    choice = get_input('Would you like to run long-term backup? (y/n) ')
    if choice == 'y':
        subprocess.check_call(
            '/usr/local/bin/rsnapshot -c ./rsnapshot.conf beta',
            shell=True
        )


def check_drive():

    clr_scr()
    # print disk info to help user
    subprocess.check_call(
        '/usr/bin/lsblk',
        shell=True
    )

    print('')
    drive = get_input('Which drive to check for smartctl? (/dev/sdx) : ')

    lines_w_metrics = subprocess.check_output(
        'smartctl ' + drive + ' -d sat -A | grep "0x00"',
        shell=True
    )

    for line in lines_w_metrics.decode('utf-8').split('\n'):
        # double check if line contains a metric
        if '0x00' in line:
            columns = line.split()
            # print only if raw_value bigger than threshold
            if columns[5] < columns[9]:
                if columns[0] in SMARTCTL_METRICS:
                    # print in red important metrics
                    print('\033[1;31m' + line + '\033[1;m')
                else:
                    # print any other metrics
                    print(line)
            else:
                print(line)

    confirm_quit('Do you want to continue? (y/n) : ')


def main():

    choice = 'y'
    while choice == 'y':
        check_drive()
        choice = get_input('Would you like to check another drive? (y/n) ')

    clr_scr()

    # prepare dir for logging
    mkdir('./log')
    mkdir('./snapshots')

    # print source and destination
    print('Source :')
    with open('rsnapshot.conf') as f:
        for line in f:
            if line.startswith('backup'):
                print(line)

    print('\n\nDestination :')
    with open('rsnapshot.conf') as f:
        for line in f:
            if line.startswith('snapshot_root'):
                print(line)

    confirm_quit(
        'THIS IS FINAL CONFIRMATION. BACKUP WILL START NOW.'
        ' Do you want to continue? (y/n) : '
    )

    run()

if __name__ == '__main__':
    main()
