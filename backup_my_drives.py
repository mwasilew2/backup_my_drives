#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess
import sys
import time

"""
TODO
- smartctl resutls saved to file in log/
- save logs not only on the destination, but on the source as well
- edit rsnapshot.conf from this script for log & snaphots dirs (ask if it's different than current)
"""

CHANGE_LOG = """
3.1
===
- parsing cli parameters
- using objects
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
3.1
"""


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


class BackupObject(object):


    def __init__(self, path):
        self.SMARTCTL_METRICS = ['5', '187', '188', '196', '197', '198']
        self.SCRIPT_PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.CONFIG_FILE = path

        self.SOURCE_LINES = []
        self.DESTINATION_LINE = ''
        self.SNAPSHOTS_DIR = ''
        self.LOG_FILE = ''
        self.LOG_DIR = ''
        self.LEVELS = []
        self.LEVELS_CONFIG = {}

        with open(self.CONFIG_FILE) as f:
            for line in f:
                if line.startswith('backup'):
                    self.SOURCE_LINES.append(line)

                if line.startswith('snapshot_root'):
                    self.DESTINATION_LINE = line
                    columns = line.split()
                    self.SNAPSHOTS_DIR = columns[1]

                if line.startswith('logfile'):
                    columns = line.split()
                    self.LOG_FILE = columns[1]
                    self.LOG_DIR = os.path.dirname(os.path.abspath(self.LOG_FILE))

                if line.startswith('retain'):
                    columns = line.split()
                    self.LEVELS.append(columns[1])
                    self.LEVELS_CONFIG[columns[1]] = columns[2]

        # run functions

        clr_scr()
        choice = get_input('check drives? (y/n) ')
        while choice == 'y':
            self.check_drive()
            choice = get_input('check another drive? (y/n) ')
        confirm_continue()

        self.prepare_and_initiate()


    def check_drive(self):

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
                    if columns[0] in self.SMARTCTL_METRICS:
                        # print in red important metrics
                        print('\033[1;31m' + line + '\033[1;m')
                    else:
                        # print any other metrics
                        print(line)
                else:
                    print(line)


    def prepare_and_initiate(self):
        check_if_bin_installed('rsnapshot')

        # print source and destination, prepare dirs
        clr_scr()
        print('\033[0;36mSources :\033[1;m')
        for source in self.SOURCE_LINES:
            print(source.rstrip())
        print('')

        print('\033[0;36mDestination :\033[1;m')
        print(self.DESTINATION_LINE.rstrip())
        print('')

        mkdir(self.LOG_DIR)
        mkdir(self.SNAPSHOTS_DIR)

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

        for level in self.LEVELS:
            print(get_rsnap_level_info(level))
        print('')

        # now that the user has been informed, ask for backup level
        levels_to_run = []
        for level in self.LEVELS:
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
        self.run_rsnapshot(levels_to_run)


    def run_rsnapshot(self,levels_to_run):

        # check config file
        try:
            subprocess.check_call(
                'rsnapshot -c ' + self.CONFIG_FILE + ' configtest',
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
                    'rsnapshot -q -c ' + self.CONFIG_FILE + ' ' + level,
                    shell=True
                )
            except subprocess.CalledProcessError as e:
                print(e)
                return


def main():
    parser = argparse.ArgumentParser(
        description='Script used for creating snapshots of filesystem',
        epilog='Example of use:\n '
        'backup_my_drives.py -c config_file.conf'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-c',
        '--config_file',
        help='provide path to the config file'
    )

    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version=VERSION,
        help='print version of the script'
    )

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    else:
        if args.config_file:
            BackupObject(args.config_file)
        else:
            print('please provide path to config file')

if __name__ == '__main__':
    main()
