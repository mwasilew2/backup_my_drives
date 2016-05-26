#!/usr/bin/python3

import os
import shutil
import subprocess
import sys
import time

"""
TODO
- smartctl resutls saved to file in log/
- cli argument parsing
- save logs not only on the destination, but on the source as well
"""

CHANGE_LOG = """
3.0
===
- moved to python 3
- using rsnapshot rather than rsync to save disk space and have full history
- using rsnapshot logging
- sticking with one approach (fully functional rather than func + oop)
- pep8 compliant
- better error handling
- better UI
- static vars at the top
- rsnapshot config file the main source of config (e.g. levels)
2.3
===
- print smartctl errors
- save to log file the list of all dirs selected
- save to log file exact rsync commands used
2.2
===
- cli arguments parsing
- change log
- name was changed from backup_script_for_my_drives_(version).py to \
backup_my_drives.py
2.1
===
- improved logging
- saving information about what changes are being made to files
"""

VERSION = """
3.0
"""

# ==========================================================================
#                   STATIC & FILE PARSING
# ==========================================================================

SMARTCTL_METRICS = ['5', '187', '188', '196', '197', '198']
SCRIPT_PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = SCRIPT_PARENT_DIR + '/rsnapshot.conf'


SOURCE_LINES = []
DESTINATION_LINE = ''
SNAPSHOTS_DIR = ''
LOG_FILE = ''
LOG_DIR = ''
LEVELS = []
LEVELS_CONFIG = {}

with open(CONFIG_FILE) as f:
    for line in f:
        if line.startswith('backup'):
            SOURCE_LINES.append(line)

        if line.startswith('snapshot_root'):
            DESTINATION_LINE = line
            columns = line.split()
            SNAPSHOTS_DIR = columns[1]

        if line.startswith('logfile'):
            columns = line.split()
            LOG_FILE = columns[1]
            LOG_DIR = os.path.dirname(os.path.abspath(LOG_FILE))

        if line.startswith('retain'):
            columns = line.split()
            LEVELS.append(columns[1])
            LEVELS_CONFIG[columns[1]] = columns[2]


# ==========================================================================
#                   LIBRARY
# ==========================================================================


def get_input(msg):
    try:
        user_input = input(msg)
    except (KeyboardInterrupt, EOFError):
        print('Bye.')
        sys.exit(0)
    return user_input


def get_rsnap_level_info(level):
    # value in config file
    level_info = level + '\tconfig: ' + LEVELS_CONFIG[level]

    # count existing snapshots
    existing_snapshots = 0
    list_of_snapshots = os.listdir(SNAPSHOTS_DIR)
    for snap in list_of_snapshots:
        if level in snap:
            existing_snapshots += 1

    level_info = level_info + '\texisting: ' + str(existing_snapshots)

    # get last mod date
    all_snaps = [SNAPSHOTS_DIR + s for s in os.listdir(SNAPSHOTS_DIR)]
    all_level_snaps = [snap for snap in all_snaps if (os.path.isdir(snap) and level in snap)]
    if all_level_snaps:
        latest_subdir = max(all_level_snaps, key=os.path.getmtime)
        last_mod_time = time.localtime(os.path.getmtime(latest_subdir))
        last_mod_time_hum = time.strftime("%Y-%m-%d %H:%M:%S, %z", last_mod_time)
    else:
        last_mod_time_hum = 'none'

    level_info = level_info + '\tlast_snap: ' + last_mod_time_hum

    # return full string
    return level_info


def confirm_continue():
    choice = get_input('continue? (y/n) : ')
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
                print('\033[0;31mFailed to create ' + path + '\033[1;m')
            else:
                print('\033[0;32m' + path + ' created.\033[1;m')
        else:
            print('\033[0;36m' + path + ' already exists! skipping...\033[1;m')
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


def check_if_bin_installed(command):

    if not shutil.which(command):
        print(command + ' not installed. Exiting.')
        sys.exit(0)
    else:
        pass

# ==========================================================================
#                   SCRIPT
# ==========================================================================


def check_drive():

    check_if_bin_installed('smartctl')
    clr_scr()

    # print disk info to help user
    subprocess.check_call(
        'lsblk',
        shell=True
    )

    # user input - select drive
    print('')
    drive = get_input('Which drive to check for SMART metrics? (/dev/sdx) : ')

    # get metrics from cli
    try:
        lines_w_metrics = subprocess.check_output(
            'smartctl ' + drive + ' -d sat -A | grep "0x00"',
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print(e)
        return

    # print SMART metrics
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


def prepare_and_initiate():
    check_if_bin_installed('rsnapshot')

    # print source and destination, prepare dirs
    clr_scr()
    print('\033[0;36mSources :\033[1;m')
    for source in SOURCE_LINES:
        print(source.rstrip())
    print('')

    print('\033[0;36mDestination :\033[1;m')
    print(DESTINATION_LINE.rstrip())
    print('')

    mkdir(LOG_DIR)
    mkdir(SNAPSHOTS_DIR)

    confirm_continue()

    # everything is ready at this point, we need to get levels from user
    # inform how levels work in rsnapshot
    clr_scr()
    info = 'Rotation on every level happens regardless if highest snapshot ' +\
        'from previous level is available. ' +\
        'New snapshot on every level is created only if highest snapshot ' +\
        'from previous level is available. ' +\
        'Only first level actually backs up any files from the file system,' +\
        'other only rotate. ' +\
        'This means that if you run 2nd and not all 1st are available, ' +\
        'you will permanently remove highest 2nd snapshot, ' +\
        'but not create any new 2nd snapshots.\n'

    print(info)

    for level in LEVELS:
        print(get_rsnap_level_info(level))
    print('')

    # now that the user has been informed, ask for backup level
    levels_to_run = []
    for level in LEVELS:
        if get_input('run \033[0;32m' + level + '\033[1;m backup? (y/n) ') == 'y':
            levels_to_run.append(level)

    if not levels_to_run:
        print('Bye.')
        sys.exit(0)

    # print final confirmation
    print('')
    msg = 'THIS IS FINAL CONFIRMATION. THE FOLLOWIGN BACKUPS WILL RUN:\n'

    for level in levels_to_run:
        msg = msg + '\033[1;31m' + level.upper() + '\033[1;m\n'

    print(msg)

    confirm_continue()

    # start backup process
    run_rsnapshot(levels_to_run)


def run_rsnapshot(levels_to_run):

    # check config file
    try:
        subprocess.check_call(
            'rsnapshot -c ' + CONFIG_FILE + ' configtest',
            shell=True
        )
    except subprocess.CalledProcessError as e:
        print(e)
        return

    # run backups
    for level in levels_to_run:
        print('Starting ' + level + ' backup...')
        try:
            subprocess.check_call(
                'rsnapshot -q -c ' + CONFIG_FILE + ' ' + level,
                shell=True
            )
        except subprocess.CalledProcessError as e:
            print(e)
            return


def main():

    clr_scr()
    choice = get_input('check drives? (y/n) ')
    while choice == 'y':
        check_drive()
        choice = get_input('check another drive? (y/n) ')
    confirm_continue()

    prepare_and_initiate()

if __name__ == '__main__':
    main()
