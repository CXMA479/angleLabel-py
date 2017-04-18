#coding=utf-8
'''
      little trick
      Chen Y.Liang
      Mar 9, 2017


'''


'''
ungleUI.py   imagePath=./image/   angletFile = ./image/angleList.txt
'''

import sys,os
import logging
import matplotlib.pyplot as plt
import cv2
import numpy as np
from scipy import ndimage

class buildingUI():



	def __init__(self,imagePath,buildingPath):
		assert os.path.isdir(imagePath), 'directory of {'+imagePath+'} does not exsist.'
		assert os.path.isdir(buildingPath),'directory of {'+buildingPath+'} does not exsist.'
		self.imageList=os.listdir(imagePath)
		self.buildingList=os.listdir(buildingPath)
		self.s=len(self.buildingList)-1
		self.idx=0
		self.buildingPath=buildingPath
		self.imagePath=imagePath
		self.imageNum=len(self.imageList)
		self.exitFlag=0  #   when it equals to 2, exit.
#		print('s0:'+self.s0)

#	def is_unique(self,imageName):
#		return not( (imageName+'\t' in self.s0) or (imageName+'\t' in self.s))

	def begin(self):
		while True:
			if self.idx>=self.imageNum:
				return
			try:
				imageName=self.imageList[self.idx]
#				print('imageName: ',imageName+'\n')
				self.idx=self.idx+1
			except IndexError:
				1==1

			else:
				#logging.info('Draw the line')
				img=cv2.imread(self.imagePath+imageName)
				img0=img.copy()
#				print('image size: '+str(img.shape))
				img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

				'''
				------->x
				|
				|
				|y
				'''
				while True:
					try:
						plt.imshow(img)
						c=plt.ginput(timeout=-1,n=2)
						plt.close()
						x0,y0=c[0]
						x1,y1=c[1]
						x0=int(np.round(x0))
						y0=int(np.round(y0))
						x1=int(np.round(x1))
						y1=int(np.round(y1))

						cv2.line(img,(x0,y0),(x1,y1),(255,0,0),1)

						tanA=(y1-y0)/(x0-x1)
						alpha=np.arctan(tanA)/np.pi*180
						print('alpha: '+str(alpha)+'\n')
					except:   # worker wants to stop this image.
						#logging.info('Next Image')
#						print('Next  image...\n')
						self.exitFlag=self.exitFlag+1
						if self.exitFlag>=2:
							return
						break
					else:
#					print('read the image...\n')
#					print('alpha: '+str(alpha )+'\n')
						self.exitFlag=0
						imgTmp=ndimage.rotate(img,alpha)
						img0Tmp=ndimage.rotate(img0,alpha)

						plt.imshow(imgTmp)

						c=plt.ginput(timeout=-1,n=2)
						plt.close()
						try:
							x0,y0=c[0]
							x1,y1=c[1]
						except:
							break
						x0=int(np.round(x0))
						y0=int(np.round(y0))
						x1=int(np.round(x1))
						y1=int(np.round(y1))

						ltx=np.min([x0,x1])
						lty=np.min([y0,y1])
						rbx=np.max([x0,x1])
						rby=np.max([y0,y1])
						print('points: ('+str(ltx)+','+str(lty)+'), ('+\
							str(rbx)+','+str(rby)+')\n')

						patch=img0Tmp[lty:rby,ltx:rbx,:]
						cv2.imwrite(self.buildingPath+str(self.s+1)+'.png',patch)
						self.s=self.s+1














if __name__ == '__main__':

	imagePath='./image/'
	buildingPath='./building/'

	if len(sys.argv)==1: # no parameter, use default
		print('No parameter is specified, use default\n')

	elif len(sys.argv)==2: # see who is presented
		s=sys.argv[1]
		assert '=' in s , 'syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }'
		paraName,para=s.split('=')

		if 'image' in paraName:
			imagePath=para
		elif 'building' in paraName:
			buildingPath=para
		else:
			raise ValueError('syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }')

	elif len(sys.argv)==3:
		s=sys.argv[1]

		assert '=' in s , 'syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }'

		paraName,para=s.split('=')

		if 'image' in paraName:
			imagePath=para
		elif 'building' in paraName:
			buildingPath=para
		else:
			raise ValueError('syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }')

		s=sys.argv[2]
		assert '=' in s , 'syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }'
		paraName,para=s.split('=')

		if 'image' in paraName:
			imagePath=para
		elif 'building' in paraName:
			buildingPath=para
		else:
			raise ValueError('syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }')
	else:
		raise ValueError('syntax error: angleUI.py {imagePath/buildingPath}={xxx/ / building/ }')

	print('Path setting:\n\t image: '+imagePath+'\tbuildingPath: '+buildingPath)


	it=buildingUI(imagePath,buildingPath)

	it.begin()   # never return...

	print('Done.\n')



