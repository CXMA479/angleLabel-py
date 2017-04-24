#coding=utf-8
'''
      little trick
      Chen Y.Liang
      Mar 9, 2017


'''


'''
ungleUI.py   imagePath=./image/   angleFile = ./image/angleList.txt
'''

import sys,os
import logging
import matplotlib.pyplot as plt
import cv2
import numpy as np
from scipy import ndimage

import argparse




class angleUI(object):
	"""
define the format of the output:
imageIdx.type\tlabel\tcenterPoint(x,y)\tangle(degree) of the longer side\thalf of the longer side's length\thalf of the shorter side;\t...\n

short as:
imgIdx\tlabel\tx,y\tangle\trh\trw;\tlabel\tx,y\t...\n



note:
             1. the index of image starts from 0.
             2. each image should be renamed by ascending order.
	     3. there are only one type of images in a folder.
	     4. angle is related to rh.

	"""
	def __init__(self,imagePath,angleFile):
		"""
		imagePath: string, containing images to label
		angleFile: string, file of the output, if already exists, read the labeled images and ignore them
		"""
		assert os.path.exists(imagePath),imagePath+' not exist'
		self.imgPath=imagePath
		if imagePath[-1] != '/':
			self.imgPath += '/'

		self.fh=open(angleFile,'a+')
		self.fs=self.fh.readlines()
		self.currentIdx=len(self.fs)  # everytime read an image by this indication
		self.imgList=os.listdir(imagePath)
		self.imgNum=len(self.imgList)
		assert self.imgNum-1 > self.currentIdx   # exclude the '\n'
		self.imgExtFlag=False  # switch to next img
		self.imgRaw=0
		self.imgType=self.imgList[0].split('\t')[0].split('.')[1] # get the suffix
		self.imgTmp=0

		self.x,self.y,self.alpha,self.rh,self.rw=0,0,0,0,0
		self.p1=(0,0)
		self.p2=(0,0)
		self.p3=(0,0)

		self.s=""  # output of this run, will be write to the file
		self.angleFile=angleFile


	def begin(self):
		"""
	follow chart:
		1. get two points of the img
		2. draw a line
		3. draw the perpendicular line through the midpoint
		4. get another one point on the perpendicular line
		5. draw the box
		6. wait the usr's decision: drop/save
		7. convert the inputs to the std format:
                                                         (x,y) alph(deg) rh rw
		8. write to the file
		9. whether to present next img?

	further features:
		1. enable modifying previous labelings with specific img index.
		"""

		rL=100 # perpendicular line length for each side
		while self.currentIdx < self.imgNum:
			print self.imgPath+str(self.currentIdx)+'.'+self.imgType
			self.imgRaw=cv2.imread(self.imgPath+str(self.currentIdx)+'.'+self.imgType)
			self.imgRaw=cv2.cvtColor(self.imgRaw,cv2.COLOR_BGR2RGB)

			self.imgTmp=self.imgRaw.copy()
			self.imgSave=self.imgTmp.copy()
			self.imgExtFlag=False

			self.s += str(self.currentIdx)+'.'+self.imgType

			while ~ self.imgExtFlag:
				plt.clf()     # avoid heavy load !
				plt.title(' 1st point(left) \ next img(middle click)')
				plt.imshow(self.imgTmp)
				self.p1=np.array(plt.ginput(timeout=-1,n=1))
				if list(self.p1) == []:
					self.imgExtFlag=True
					self.s +='\n'
					break
					continue

				plt.title('2nd point(left) \ next img(middle click)')

				self.p2=np.array(plt.ginput(timeout=-1,n=1))
				if list(self.p2) == []:
					self.imgExtFlag=True
					self.s +='\n'
					break
					continue

				"""
					1. calculate alpha (deg, starts from x axis, clockwise)
					2. draw the line
				"""
				self.p1=self.p1[0]
				self.p2=self.p2[0]
#				print self.p1,self.p2
				y=self.p2[1]-self.p1[1]
				x=self.p2[0]-self.p1[0]
				tang=y*1./(x+np.exp(-4))
				self.alpha=np.arctan(tang) #   in final stage, convert it to degree
				midP=(self.p1+self.p2)/2.
				midDir=np.array([np.cos(self.alpha+np.pi/2), np.sin(self.alpha+np.pi/2)])
				p3=midP+rL*midDir
				p4=midP-rL*midDir

				imgMid=self.imgTmp.copy()

				self.p1,self.p2,p3,p4= [ np.array([ np.int(np.round(varx[0])),np.int(np.round(varx[1]))]) for varx in [self.p1,self.p2,p3,p4] ]

				# draw p1-p2, p3-p4
				plt.clf()

				cv2.line(imgMid,tuple(self.p1),tuple(self.p2),(250,0,0),1)
				cv2.line(imgMid,tuple(p3),tuple(p4),(0,250,0),1)
				plt.imshow(imgMid)
				# get the 3rd point
				plt.title('3nd click')
				self.p3=np.array(plt.ginput(timeout=-1,n=1))[0]

				# calculate height
				dirL=self.p3-midP
				w=np.dot(dirL,midDir)
				# draw the box: 
				shift=w*midDir
				w=np.abs(w)

				p1_shift=self.p1+shift
				p2_shift=self.p2+shift


				p1_shift,p2_shift= [ np.array([ np.int(np.round(varx[0])),np.int(np.round(varx[1]))]) for varx in [p1_shift,p2_shift] ]
				plt.clf()     # do this for every display !
				cv2.line(self.imgTmp,tuple(self.p1),tuple(self.p2),(250,0,0),1)
				cv2.line(self.imgTmp,tuple(self.p2),tuple(p2_shift),(250,0,0),1)
				cv2.line(self.imgTmp,tuple(p2_shift),tuple(p1_shift),(250,0,0),1)
				cv2.line(self.imgTmp,tuple(p1_shift),tuple(self.p1),(250,0,0),1)
				plt.imshow(self.imgTmp)

				# whether to save?
				plt.title( '[save \ drop]: right click \ middle click\n')
#				try:
#					label=int(label_s)
				label=1

				if plt.ginput(timeout=-1,n=1) != []: # save it
					# calculate the center point
					rw=np.int(np.round(w/2.))
					rh=np.int(np.round(np.sqrt(x**2 + y**2)))


					cenP= midP+w/2*midDir
					cenP=  np.array( [ np.int(np.round(cenP[0])), np.int(np.round(cenP[1]))])


					self.s= self.s +';\t'+str(label)+'\t'+str(cenP[0])+','+str(cenP[1])+'\t'+str(self.alpha*180./np.pi)+'\t'+str(rh)+'\t'+str(rw)


					# modify imgSave: draw the latest box
					cv2.line(self.imgSave,tuple(self.p1),tuple(self.p2),(250,0,0),1)
					cv2.line(self.imgSave,tuple(self.p2),tuple(p2_shift),(250,0,0),1)
					cv2.line(self.imgSave,tuple(p2_shift),tuple(p1_shift),(250,0,0),1)
					cv2.line(self.imgSave,tuple(p1_shift),tuple(self.p1),(250,0,0),1)

				self.imgTmp=self.imgSave.copy()
				self.imgMid=self.imgSave.copy()
			# next box


			# write to the file and save it.
			self.fh.write(self.s)
			self.fh.close()
			self.s=''

			self.fh=open(self.angleFile,'a+')

			self.currentIdx +=1
			# next image
















def parse_args():
	parser=argparse.ArgumentParser(description='specify the paths')
	parser.add_argument('--imgP',dest='imgPath',help='directory containing images to label',default='../img',type=str)
	parser.add_argument('--outF',dest='outPath',help='file to store the output (including the path)',default='../angleList.txt',type=str)
#	parser=add_argument('--
	args=parser.parse_args()
	return args





if __name__ == '__main__':



#	it=buildingUI(imagePath,buildingPath)

	args=parse_args()


	
#	print args.imgPath,args.outPath
#	return

	it=angleUI(args.imgPath,args.outPath)

	it.begin()   # never return...

	print('Done.\n')



