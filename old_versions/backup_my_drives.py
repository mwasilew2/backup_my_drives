#!/usr/bin/python

"""The purpose of this script is to simplify backup tasks. Linux command
rsync is used to ensure that an exact copy is created (e.g. attributes
mirrored, files deleted).
"""

import os
import sys
from datetime import datetime
import argparse

# subprocess is supposed to replace some of the above
import subprocess


WARNING_MSG = """
Be extremely careful! If destination contains more data than source it
will be deleted permanently from your back up (it will be mirrored)!!!!!
This is done in order to release space on the drive.

Do you understand the risk?
"""

CONFIRM_SINGLE_MSG = """
Do you want the following directory to be saved:"""

CONFIRM_ALL_MSG = """
Confirm that you want all of the following directories to be mirrored!!!
(one final confirmation for the entire list, after pressing y and enter back up will start)
"""

START_MSG = """
=================================
Back up task started. Please wait... (You can monitor the process by looking at logs in log/)
"""

CHANGE_LOG = """
2.1
===
- improved logging, saving information about what changes are being made to files

2.2
===
- cli arguments parsing
- change log
- name was changed from backup_script_for_my_drives_(version).py to backup_my_drives.py

2.3
===
- print smartctl errors
- save to log file the list of all dirs selected
- save to log file exact rsync commands used

"""

VERSION = """
2.3
"""




def confirm(msg):
    """Method used to get confirmation from the user.
    First print message to the screen. Than ask for confirmation.
    If y is pressed return 'go'.
    """

    # print message
    print ''
    print msg

    # read input from user
    try:
        choice = raw_input('Type y to continue: ')
    except (KeyboardInterrupt, EOFError): # Suppress keyboard interrupt
        print '\n\n  Bye.\n'
        sys.exit(0)

    # return value
    if choice == 'y':
        return 'go'
    else:
        pass


class BackupFunctions(object): #pylint: disable=R0903
    """Main class"""

    source = '/media/truecrypt1/'
    destination = '/media/truecrypt2/'


    # prepare for logging
    if not os.path.exists("./log"):
        os.makedirs("./log")

    i = datetime.now()
    log_file_name = i.strftime('%Y_%m_%d_%H%M%S') + '.log'
    log_location = '/media/truecrypt2/log/'
    log_location_name = log_location + log_file_name



    def __init__(self):



        # list of directories to copy
        self.list_of_dirs = [

            # be careful, directories in this list will be mirrored
            # exactly!!!!!!!!!!!!!!!!!!!!!!!!
            # i.e. if directory on the destination contains more content
            #  than on the source it will be deleted!!!!!!!!!!

            # 1_home
            '1_home/',

            # 2_data
            # '2_data/archive/',
            # '2_data/english/',
            # '2_data/library-courses-materials/',
            # '2_data/PHOTO/'

        ]

        self.list_to_run = []

        # check the drive
        os.system('clear')
        drive = raw_input('Which drive to check for smartcl?: ')
        os.system('echo "Checking drive ' + drive + ' for smartctl..."')
        os.system("smartctl " + drive + " -d sat -l error")
        metrics = subprocess.check_output("smartctl " + drive + " -d sat -A | grep \"0x00\"", shell=True)
        # RED='\033[0;31m';NC='\033[0m';IFS=$'\n';for i in `smartctl /dev/sdb -d sat -A | grep "0x00"`; do NR=$(echo $i | awk '{print $1}'); VAL=$(echo $i | awk '{print $10}'); THR=$(echo $i | awk '{print $6}'); if [ "$VAL" -gt "$THR" ];then if [ "$NR" == 5 ] || [ "$NR" == 187 ] || [ "$NR" == 188 ] || [ "$NR" == 196 ] || [ "$NR" == 197 ] || [ "$NR" == 198 ]; then echo -en "${RED}";echo $i; echo -en "${NC}"; else echo $i; fi; fi ; done
        important_metrics = ['5', '187', '188', '196', '197', '198']

        for line in metrics.split('\n'):
            # if the line contains metric value
            if "0x00" in line:
                columns = line.split()
                # if raw_value bigger than threshold
                if columns[5] < columns[9]:
                    # print in red important metrics
                    if columns[0] in important_metrics:
                        print '\033[1;31m' + line + '\033[1;m'
                    else:
                        print line


        # cli_command = "RED=\'\\033[0;31m';NC='\\033[0m';IFS=$'\\n';for i in " + metrics + "; do NR=\$(echo \$i | awk '{print \$1}'); VAL=\$(echo \$i | awk '{print \$10}'); THR=\$(echo \$i | awk '{print \$6}'); if [ \"\VAL\" -gt \"\$THR\" ];then if [ \"\$NR\" == 5 ] || [ \"\$NR\" == 187 ] || [ \"\$NR\" == 188 ] || [ \"\$NR\" == 196 ] || [ \"\$NR\" == 197 ] || [ \"\$NR\" == 198 ]; then echo -en \"\${RED}\";echo \$i; echo -en \"\${NC}\"; else echo \$i; fi; fi ; done'"
        
        # os.system(cli_command)
        if confirm('Do you want to continue?') == 'go':
            pass
        else:
            print '\n\n  Bye.\n'
            sys.exit(0)


        # make sure that user knows how this coppying works
        os.system('clear')
        if confirm(WARNING_MSG):

            # go through the list and ask the user whether to copy an entry
            os.system('clear')
            print 'Full list:'
            for entry in self.list_of_dirs:
                print entry

            print CONFIRM_SINGLE_MSG
            for dir_to_confirm in self.list_of_dirs:
                if confirm(dir_to_confirm) == 'go':
                    self.list_to_run.append(dir_to_confirm)


            if self.list_to_run:
                # one more confirmation. Just in case.
                os.system('clear')
                print CONFIRM_ALL_MSG
                for cmd in self.list_to_run:
                    print cmd
                if confirm(''):
                    self.run()
                else:
                    print '\n\n  Backup task has been canceled. Bye.\n'
            else:
                print '\n\n  Backup task has been canceled. Bye.\n'

        else:
            print '\n\n  Backup task has been terminated. Nothing was done. Bye.\n'


    def run(self):
        """Here is the core functionality."""

        if not self.list_to_run:
            print '\n\n  Nothing to do. List empty. Bye.\n'

        else:
            print START_MSG


            for confirmed_entry in self.list_to_run:
                os.system("echo '" + confirmed_entry + "' >> " + self.log_location_name)


            for confirmed_entry in self.list_to_run:
                try:

                    os.system("echo '" + confirmed_entry + "' >> " + self.log_location_name)
                    os.system("echo ' ' >> " + self.log_location_name)

                    # Here is the core command
                    command = 'rsync -vvcazhi --delete-after --stats --progress ' + \
                    self.source + confirmed_entry + ' ' + \
                    self.destination + confirmed_entry + \
                    ' >> ' + self.log_location + self.log_file_name + ' 2>&1'

                    os.system("echo '" + command + "' >> " + self.log_location_name)

                    result = os.system(command)
                    if result != 0:
                        print confirmed_entry + \
                        " failed. See log files for more information."
                        print ''

                except (KeyboardInterrupt, EOFError):
                    # Suppress keyboard interrupt
                    print '\n\n  Bye.\n'
                    sys.exit(0)

def main():
    """ Main method, used only to instantiate an object. All logic is in
    the constructor.
    """
    parser = argparse.ArgumentParser(description='Tool used for making backups.')
    parser.add_argument('-V', '--version', action='version', version=VERSION)
    args = parser.parse_args()

    instance = BackupFunctions() #pylint: disable=W0612

if __name__ == '__main__':
    main()

