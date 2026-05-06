#!/usr/bin/env python

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import argparse

def imdisp(data):
     plt.imshow(data,vmin=np.median(data)-np.std(data),vmax=np.median(data)+np.std(data),origin='lower')
     #plt.imshow(data,vmin=950, vmax = 3000, origin='lower')


parser = argparse.ArgumentParser(description = 'examine top rows of IM3 (Q1) on MODS2R')
parser.add_argument("infile",help="input datafile")
parser.add_argument("extn",type=int,help="Archon ADC IM#")
args = parser.parse_args()
infile = args.infile 
ext = args.extn

#b6 = fits.open("/Volumes/repository/20260503/mods2r.20260504.0006.fits")
#b7 = fits.open("/Volumes/repository/20260503/mods2r.20260504.0007.fits")
image = fits.open(infile)

fname = infile.split("/")[-1]
pngfile = fname[:fname.find(".fits")] + "_IM" + str(ext) + ".png"


d = image[ext].data

fig,ax=plt.subplots(2,1)

ovrscn = d[:,1544:1576]
datareg = d[:,1500:1532]
x = np.arange(1544)

ylim1 = np.median(datareg) - 10
ylim2 = np.median(datareg) + 10
ax[0].set_ylim(ylim1,ylim2)
ax[0].plot(x,np.mean(ovrscn,axis=1),c="k",ds="steps-mid",lw=2,label="overscan, averaged along rows")
ax[0].plot(x,np.mean(datareg,axis=1),c="r",ds="steps-mid",ls="dotted",label="32 cols of data, averaged along rows")
ax[0].set_xlabel("Rows")
ax[0].set_ylabel("Row-Average Counts [ADU]")
ax[0].legend()

if ext==3 or ext==4:
   xlim1 = 1540
   xlim2 = 1544
if ext==1 or ext==2:
   xlim1 = 0
   xlim2 = 4
ax[1].set_xlim(xlim1,xlim2)
ax[1].plot(x,np.mean(ovrscn,axis=1),c="k",ds="steps-mid",lw=2,label="overscan, averaged along rows")
ax[1].plot(x,np.mean(datareg,axis=1),c="r",ds="steps-mid",ls="dotted",label="32 cols of data, averaged along rows")
ax[1].legend()
ax[1].set_xlabel("Rows")
ax[1].set_ylabel("Row-Average Counts [ADU]")

plt.suptitle(("%s[IM%d]") % (infile,ext))

plt.savefig(pngfile)
