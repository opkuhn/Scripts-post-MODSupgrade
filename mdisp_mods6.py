#!/usr/bin/env python

import numpy as np
import pyds9 as ds9
#import ds9 as ds9
import shlex
import subprocess
import string as str
import os
import sys
import time
from sys import argv, exit
import getopt
import argparse



#----------------------------------------------------------------
# isds9up is taken from modsView (RPogge)

def isds9up(ds9ID):
    test = subprocess.Popen(['xpaaccess','-n',ds9ID],
                            stdout=subprocess.PIPE).communicate()[0]
    if int(test):
        return True
    else:
        return False
#----------------------------------------------------------------
# startDS9 - launch a named ds9 window
#
# Inputs:
#   ds9ID = ID ('title') of a DS9 display window to open
#
# Description:
#   Launches a named DS9 instance, making sure all of the IRAF
#   imtool pipes are suppresed so that IRAF won't interfere
#   with it (and vis-vers).  It sleeps for 2 seconds to allow
#   the tool to open.  This may have to be increased on slower
#   or more loaded systems.
#
# Author:
#   R. Pogge, OSU Astronomy Dept
#   pogge.1@osu.edu
#   2012 May 3
#

def startDS9(ds9ID):
    cmdStr = 'ds9 -fifo none -port none -unix none -title %s' % (ds9ID)
    args = shlex.split(cmdStr)
    subprocess.Popen(args)
    time.sleep(2)

#---------------------------------------------------------------------------


#
# Main Program starts here...
#


# script to display multiple new MODS images, extension 6 -opk/lbto

parser = argparse.ArgumentParser(description = 'display a set of images which are in a list')
parser.add_argument('imlist', help = 'filename of list')
parser.add_argument('extn', help = 'extension to display')
args = parser.parse_args()
inlist = args.imlist 
extn = args.extn
  

mext =True  # no option for single fits files right now

versNum='2.0'
versDate='2026-03-03'


if isds9up('mdisp'):
    disp = ds9.DS9('mdisp')
    disp.set('exit')
    print('\nmdisp ds9 window killed\n')
else:
    print('\nNo mdisp ds9 window is running, nothing to kill.\n')
#if not isds9up('mdisp'):
    startDS9('mdisp')

disp = ds9.DS9('mdisp')

afiles = np.genfromtxt(inlist,dtype="str")


cntr=0
for file in afiles:
     print ("%s" % (file))
     cntr=cntr+1 
     disp.set('frame %d' % cntr)
     disp.set('scale mode 99.5')
     disp.set('zoom to fit')
     if (mext):
        dispCmd = "file %s\\[%s\\]" % (file,extn)
     else:
        dispCmd = "file %s" % (file)
     disp.set(dispCmd)

