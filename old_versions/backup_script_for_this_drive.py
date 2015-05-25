#!/usr/bin/python

import os
import sys
from datetime import datetime

class Backup_functions():

    def __init__(self):
        # this script assumes that source directory is /media/truecrypt1, destination is /media/truecrypt2/



        # list of directories to copy
        self.list_to_copy = [

            # be careful, directories in this list will be mirrored exactly!!!!!!!!!!!!!!!!!!!!!!!!
            # i.e. if directory on the destination contains more content than on the source it will be deleted!!!!!!!!!!

            # 1_home
            '1_home/',

            # 2_data
            '2_data/archive/CERN/',

        ]

        self.list_to_run = []

        print ''
        print 'Be extremely careful! If destination contains more than source it will be mirrored (content will be deleted on destination)!!!!!'
        print ''


        for dirs_to_copy in self.list_to_copy:
            if self.Confirm(dirs_to_copy) == 'go':
                self.list_to_run.append(dirs_to_copy)

        self.Run()


    def Confirm(self,msg):
        # print command that user will confirm in a moment

        print ''
        print msg

        # read input from user
        try:
            choice = raw_input('Type y if you want to proceed: ')
        except (KeyboardInterrupt, EOFError): # Suppress keyboard interrupt
            print '\n\n  Bye.\n'
            sys.exit(0)

        if choice == 'y':
            return 'go'
        else:
            pass



    def Run(self):
        print "================================="
        print "The following directories will be copied:"
        
        for cmd in self.list_to_run:
            print cmd
        print ""

        if self.Confirm(''):
            print "================================="
            print 'Back up task started. Please wait... (You can find logs in log/)'
            print ''

        i = datetime.now()

        log_file_name = i.strftime('%Y_%m_%d_%H%M%S') + '.log'

        for confirmed_entry in self.list_to_run:
            try:
                result = os.system('rsync -arucvzh --delete-after --stats /media/truecrypt1/' + confirmed_entry + ' /media/truecrypt2/' + confirmed_entry + ' >> /media/truecrypt2/log/' + log_file_name + ' 2>&1')
                if result != 0:
                    print confirmed_entry + " failed. See log files for more information."
                    print ''
            except (KeyboardInterrupt, EOFError): # Suppress keyboard interrupt
                print '\n\n  Bye.\n'
                sys.exit(0)

def main():
    instance = Backup_functions()

if __name__ == '__main__':
    main()

