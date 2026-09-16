#!/usr/bin/env python

"""

 Find calibrations in path over time interval in days
 bias8K
 bias3K
 slitless dual
 slitless red
 slitless blue
 slitflat slitwidth  

"""

import numpy as np
from astropy.io import fits
from datetime import datetime, timedelta
import argparse
import glob


parser = argparse.ArgumentParser(description='Find MODS Calibrations')
parser.add_argument('daysback', type=int, help = 'Go back <daysback> days')         
parser.add_argument('instr', type=str, help = 'mods1b, mods1r, mods2b or mods2r')
parser.add_argument('caltype', type=str, help = 'biasNK (N=3,4,8),slitless,imflatF (F=u,g,r,i,z) or slit# (slit0.6, slit2.4)')
# optional, default to "dual"
parser.add_argument('mode', nargs="?", type=str, default="dual", help = 'mode: dual, red or blue')
# optional, default to 1 x 1 unbinned
parser.add_argument('binx', nargs="?", type=int, default=1, help = 'ccdxbin')
parser.add_argument('biny', nargs="?", type=int, default=1, help = 'ccdybin')
                        
args = parser.parse_args()


daysback = args.daysback
mode = args.mode  
instr = args.instr
caltype = args.caltype

binx = args.binx
biny = args.biny

if caltype.startswith("imflat"):
     filter = str.lower(caltype[caltype.find('imflat')+len('imflat')])

if caltype.startswith("bias"):
     roi = int(str.lower(caltype).strip("biask")) # will be 8, 3, 4

#pth = "/Volumes/repository/"
pth = "/lbt/data/repository/"

utdate=[]
today = datetime.now()
b = np.arange(daysback)
for i in range(len(b)):
     back = int(b[i])
     dtback = (today-timedelta(days = back))
     utdate.append(datetime.strftime(dtback,"%Y%m%d"))

print("Searching for %s %s %s calibrations from %s to now" % (instr, mode, caltype, datetime.strftime(dtback,"%Y%m%d")))

naxis = {8:4178,3:1576,4:2048}

for j in range(len(utdate)):
     calist = []

     ddir = pth + utdate[j] + "/"
     all = glob.glob(ddir+instr+"*")

     im = [fits.open(img) for img in all]
     for i in range(len(im)):
         instrume = im[i][0].header["instrume"]
         dichname = im[i][0].header["dichname"]
         maskname = im[i][0].header["maskname"]
         gratname = im[i][0].header["gratname"]
         imagetyp = im[i][0].header["imagetyp"]
         maskpos = im[i][0].header["maskpos"]
         filtname = im[i][0].header["filtname"]
         filename = im[i][0].header["filename"]
         naxis1 = im[i][1].header["naxis1"]
         ccdxbin = im[i][0].header["ccdxbin"]
         ccdybin = im[i][0].header["ccdybin"]

         fullfile = pth + utdate[j] + "/" + filename

         if caltype.startswith("bias"):
            if str.lower(instrume) == instr and str.upper(imagetyp) == "BIAS" and naxis1*ccdxbin == naxis[roi] and ccdxbin == binx and ccdybin == biny:
               print("%s %s %s %s %s %s" % (filename,imagetyp,maskname,maskpos,gratname,filtname))
               calist.append(fullfile)

         if caltype == "slitless" and ccdxbin == binx and ccdybin == biny:
            if str.lower(instrume) == instr and str.lower(dichname) == mode and maskname == "Imaging" and gratname.startswith("G") and str.upper(imagetyp) == "FLAT":
               print("%s %s %s %s %s" % (filename,maskname,maskpos,gratname,filtname))
               calist.append(fullfile)

         if caltype.startswith("imflat") and filtname.strip("sdss_") == filter and ccdxbin == binx and ccdybin == biny:
            filter = str.lower(caltype[caltype.find('imflat')+len('imflat')])
            if str.lower(instrume) == instr and str.lower(dichname) == mode and maskname == "Imaging" and gratname.startswith("F") and str.upper(imagetyp) == "FLAT" and maskpos == "IN":
               print("%s %s %s %s %s" % (filename,maskname,maskpos,gratname,filtname))
               calist.append(fullfile)

         if caltype.startswith("slit") and ccdxbin == binx and ccdybin == biny: 
            slitwidth = caltype.strip("slit")
            if slitwidth != "5":
                 mask = "LS5x60x" + slitwidth
            elif slitwidth == "5":
                 mask = "LS60x5"
            if str.lower(instrume) == instr and str.lower(dichname) == mode and maskname == mask and gratname.startswith("G") and str.upper(imagetyp) == "FLAT" and ccdxbin == binx and ccdybin == biny:
               print("%s %s %s %s %s %s" % (filename,maskname,maskpos,gratname,filtname,mask))
               calist.append(fullfile)

     if len(calist) > 0:
         if caltype.startswith("imflat"):
            outfile = caltype[:len('imflat')] + "_" + utdate[j] + "_" + instr + "_" + mode + "_" + filter + "_" + str(binx) + "x" + str(biny) + ".list"
         elif caltype.startswith("bias"):
            outfile = caltype + "_" + utdate[j] + "_" + instr + "_" + str(binx) + "x" + str(biny) + ".list"
         else: 
            outfile = caltype + "_" + utdate[j] + "_" + instr + "_" + mode + "_" + str(binx) + "x" + str(biny) + ".list"
         np.savetxt(outfile,calist,fmt="%s")
