#Grab removable media and download files

import os
import sys
import ctypes
import itertools
import string
import platform
import time
import datetime
import argparse
from distutils import dir_util
import shutil

parser = argparse.ArgumentParser(prog="driveSnatcher")
parser.add_argument("-e", "--extensions", help="if present will filter downloads to only those of these extensions", required=False, nargs="+", default=[])
parser.add_argument("-q", "--quiet", action="store_true", help="runs in quiet mode ( No Output )", required=False)
parser.add_argument("-d", "--destination", help="destination directory for cloned drives", required=True, nargs=1)
parser.add_argument("-k", "--keywords", help="download files with specified keywords", required=False, nargs="+", default=[])
args = parser.parse_args()

#http://stackoverflow.com/questions/4188326/in-python-how-do-i-check-if-a-drive-exists-w-o-throwing-an-error-for-removable
def get_available_drives():
    if 'Windows' not in platform.system():
        return []
    drive_bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
    return list(itertools.compress(string.ascii_uppercase,
               map(lambda x:ord(x) - ord('0'), bin(drive_bitmask)[:1:-1])))


if not os.path.isdir(args.destination[0]):
    if not args.quiet:
        print "[!] Error: Destination not a directory"
    sys.exit(-1)

original_drives = get_available_drives()
count = 0
if args.extensions:
    [x.lower() for x in args.extensions]
if args.keywords:
    [x.lower() for x in args.keywords]

if not args.quiet:
    print "Running..."

while 1:
    temp = get_available_drives()
    if not temp == original_drives:
        drives = list(set(temp) - set(original_drives))
        for d in drives:

            if not args.quiet:
                print "Snatching drive " + str(d)
            count+=1
            d+=":\\"

            destination = str(time.strftime("%Y%m%d-%H%M%S"))
            os.makedirs(destination)

            if args.extensions or args.keywords:
                id = 0
                for r, d, file in os.walk(d):

                    for f in file:
                        fname, fextension = os.path.splitext(f)

                        if fextension.lower() in args.extensions or any(a in fname.lower() for a in args.keywords):
                            #\\?\ extends character limit? Thanks timmy
                            #copy2 to preserve metadata
                            shutil.copy2(os.path.join(r, f), os.path.join("\\\?\\" + args.destination[0], os.path.join(destination, fname + "_" + str(id) + fextension)))
                        id+=1
            else:
                dir_util.copy_tree(d, os.path.join(args.destination[0], str(time.strftime("%Y%m%d-%H%M%S"))))

        if not args.quiet:
            print "Running..."

    time.sleep(1)

    original_drives = temp

