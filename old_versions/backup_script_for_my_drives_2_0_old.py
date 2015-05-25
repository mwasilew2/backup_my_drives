#!/usr/bin/python

# ideas for features: write messages in color
"""The purpose of this script is to simplify backup tasks. Linux command
rsync is used to ensure that an exact copy is created (e.g. attributes
mirrored, files deleted).
"""

import os
import sys
from datetime import datetime


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

            # 2_data/
            # '2_data/archive/CERN/',
            # '2_data/english/',
            # '2_data/library-courses-materials/',
            # '2_data/PHOTO/'

        ]

        self.list_to_run = []

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
                try:

                    os.system("echo '" + confirmed_entry + "' >> " + self.log_location_name)
                    os.system("echo ' ' >> " + self.log_location_name)

                    # Here is the core command
                    command = 'rsync -arucvzh --delete-after --stats ' + \
                    self.source + confirmed_entry + ' ' + \
                    self.destination + confirmed_entry + \
                    ' >> ' + self.log_location + self.log_file_name + ' 2>&1'

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
    instance = BackupFunctions() #pylint: disable=W0612

if __name__ == '__main__':
    main()

