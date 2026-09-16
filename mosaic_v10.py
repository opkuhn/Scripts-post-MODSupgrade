#!/usr/bin/env python

from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os


# between v3 and v4, overscan is calculated differently. In v3, row-by-row and in v4, a constant for the
# whole region ("S")
# v(3,4).1 use 32 col of overscan while v(3,4) used value of 30. 
# v5. Trims by nctrim col and uses ncovrscn columns of overscan.
# v6. Set overscan to the correct value of 32, but do not use the 1st 2 columns of it or the top/bottom row
# and use median, and trim 32 columns
# v9. 32 columns of overscan. Do not use the 1st 2 columns of it or 8 rows at the top when 
#        computing overscan.
#     Trim the 50 columns of prescan only for the full-frame 8K x 3K


def imdisp(data):

     plt.imshow(data,vmin=np.median(data)-np.std(data),vmax=np.median(data)+np.std(data),origin='lower')

def mkmos(infile):

     # filename of new image to be created
     newimage = os.path.splitext(infile)[0].split("/")[-1] + "_mos_v" + versNum + ".fits"

     hdul =  fits.open(infile)
     phead = hdul[0].header
     q1 = hdul[1].data
     q2 = hdul[2].data
     q3 = hdul[3].data
     q4 = hdul[4].data
     
     (ny,nx) = q1.shape
     ncovrscn = 32
     xtrim = nx - ncovrscn

# Very quick-and-dirty approach - disregards binning and is not exact

     if ny < 8000:
           prescan = 0
     else: 
           prescan = 50

     # look for all-0's along bottom n and top n rows, excluding overscan
     n=8
     b0q1 = np.mean(q1[:n,:xtrim])
     t0q1 = np.mean(q1[ny-n:ny,:xtrim])
     b0q2 = np.mean(q2[:n,:xtrim])
     t0q2 = np.mean(q2[ny-n:ny,:xtrim])
     b0q3 = np.mean(q3[:n,:xtrim])
     t0q3 = np.mean(q3[ny-n:ny,:xtrim])
     b0q4 = np.mean(q4[:n,:xtrim])
     t0q4 = np.mean(q4[ny-n:ny,:xtrim])
     #print ("mean values along top %d and bottom %d rows:\n" % (n,n))
     #print ("im3 Q1 %.2f %.2f\n" % (b0q3,t0q3))
     #print ("im4 Q2 %.2f %.2f\n" % (b0q4,t0q4))
     #print ("im1 Q3 %.2f %.2f\n" % (b0q1,t0q1))
     #print ("im2 Q4 %.2f %.2f\n" % (b0q2,t0q2))
     
     # subtracting the median within the 'restricted' overscan region and trimming
     # ncovrscn of overscan
     # ncrej = reject ncrej first columns of the overscan when computing its median
     ncrej = 8
     ovrscn1 = np.median(q1[n:ny-1,nx-(ncovrscn-ncrej):nx])
     ovrscn2 = np.median(q2[n:ny-1,nx-(ncovrscn-ncrej):nx])
     ovrscn3 = np.median(q3[n:ny-1,nx-(ncovrscn-ncrej):nx])
     ovrscn4 = np.median(q4[n:ny-1,nx-(ncovrscn-ncrej):nx])
     sigovrscn1 = np.std(q1[n:ny-1,nx-(ncovrscn-ncrej):nx],ddof=1)
     sigovrscn2 = np.std(q2[n:ny-1,nx-(ncovrscn-ncrej):nx],ddof=1)
     sigovrscn3 = np.std(q3[n:ny-1,nx-(ncovrscn-ncrej):nx],ddof=1)
     sigovrscn4 = np.std(q4[n:ny-1,nx-(ncovrscn-ncrej):nx],ddof=1)
     q1t = q1[:,prescan:xtrim] - ovrscn1 
     q2t = q2[:,prescan:xtrim] - ovrscn2
     q3t = q3[:,prescan:xtrim] - ovrscn3
     q4t = q4[:,prescan:xtrim] - ovrscn4
     #q1t = q1[:,:xtrim] - np.median(q1[n:ny-n,nx-(ncovrscn-2):nx])
     #q2t = q2[:,:xtrim] - np.median(q2[n:ny-n,nx-(ncovrscn-2):nx])
     #q3t = q3[:,:xtrim] - np.median(q3[n:ny-n,nx-(ncovrscn-2):nx])
     #q4t = q4[:,:xtrim] - np.median(q4[n:ny-n,nx-(ncovrscn-2):nx])
     
     # changing the mapping: 1<->3 and 2<->4
     # and flipping 1 and 3 along columns, 
     # but 2 and 4 along both rows and columns
     nq1 = np.flipud(q3t)
     nq2 = np.flipud(np.fliplr(q4t))
     nq3 = np.flipud(q1t)
     nq4 = np.flipud(np.fliplr(q2t))
     
     # combining
     xxtrim = xtrim-prescan # minus 50 prescan columns 
     mosaic = np.zeros((ny*2,xxtrim*2))
     mosaic[:ny,:xxtrim] = nq1
     mosaic[:ny,xxtrim:] = nq2
     mosaic[ny:,:xxtrim] = nq3
     mosaic[ny:,xxtrim:] = nq4
     
     hdu = fits.PrimaryHDU()
     hdr6 = hdul[6].header
     hdr6['HISTORY'] = ('Overscan subtracted and merged by mosaic_v%s %s' % (versNum,versDate))
     hdr6['BIASQ1'] = ovrscn3
     hdr6['SIGBSQ1'] = sigovrscn3
     hdr6['BIASQ2'] = ovrscn4
     hdr6['SIGBSQ2'] = sigovrscn4
     hdr6['BIASQ3'] = ovrscn1
     hdr6['SIGBSQ3'] = sigovrscn1
     hdr6['BIASQ4'] = ovrscn2
     hdr6['SIGBSQ4'] = sigovrscn2
     hdu.header=hdr6
     hdu.data = mosaic
     fits.writeto(newimage,hdu.data,hdu.header,overwrite=True)

     #imdisp(mosaic)
     #plt.show()
     return newimage

 #--- main begins here ---


parser = argparse.ArgumentParser(description='reformat MODS image')
group = parser.add_mutually_exclusive_group()
group.add_argument('--image', type=str, dest='inImage', help = 'input image')
group.add_argument('--list', type=str, dest='inList', help = 'input list of images')
args = parser.parse_args()

versNum = '10'
versDate = '2026-05-01'

if args.inImage:
   inImage = args.inImage
   print ("input image is %s" % (inImage))
   #nstr = len(str.split(inImage,"."))
   #outFile = ".".join(str.split(inImage)[:(nstr-1)]) + "_out.txt"
   nimgs = 1
   mkmos(inImage)

if args.inList:
   inList = args.inList
   print ("input image list is %s" % (inList))
   #nstr = len(str.split(inList,"."))
   #outFile = ".".join(str.split(inList)[:(nstr-1)]) + "_out.txt"
   imglist = np.genfromtxt(inList,dtype=str)
   nimgs = len(imglist)
   for i in range(nimgs):
     inImage = imglist[i]
     mkmos(inImage)
