#In this file I will achieve convert skeleton data to keyboard
import os

import pykinect
from pykinect import nui
from pykinect.nui import JointId
from tools import *
from keyboard import *
from mouse import *

MOUSESENSITY=30

#Olr
HeadShoulder_lr=(
    JointId.Head,
    JointId.ShoulderCenter,
    JointId.ShoulderLeft
)
#Ofb
HeadShoulder_fb=(
    JointId.Head,
    JointId.ShoulderCenter,
    JointId.HipCenter
)

#Oleft
LeftHandElbow=(
    JointId.HandLeft,
    JointId.ElbowLeft,
    JointId.ShoulderLeft
)

#Oright
RightHandElbow=(
    JointId.HandRight,
    JointId.ElbowRight,
    JointId.ShoulderRight
)

#Oshoulder
####!!!changed, Dshoulder
LRshoulder=(
    JointId.ShoulderLeft,
    JointId.ShoulderRight
)
UDshoulder=(
    JointId.ShoulderCenter,
    JointId.HipCenter
)
ShiftLeg=(
    JointId.KneeLeft,
    JointId.KneeRight
)


class GestureController:

    def __init__(self,mouse):
        self.initReady=False
        self.frameNum=10
        self.gestureSensitivity=1
        self.KeyStatus={
            'w':False,
            's':False,
            'a':False,
            'd':False,
            'space':False,
            'alt':False,
            'q':False,
            'shift':False,
            'left':False,
            'right':False
        }
        self.frameDataQueue=[]
        self.lsInit=False
        self.mouse=mouse
        self.configInit={'Ofb': 166.01767266657541, 'Olr': 120.72047384629195, 'Dleg': 0.03453516960144043, 'Oright': 166.73018741249746, 'accSpace': -0.3980497419834137, 'Dview_lr': 0.0016001462936401367, 'Oleft': 169.31255281157834, 'accAlt': 0.0845213308930397, 'Dview_ud': 0.048435091972351074}

    def setConfigInit(self,configDict):
        self.configInit=configDict
        self.lsInit=True

    def isInit(self):
        return self.lsInit

    def notSameFrame(self,frameData):
        length=len(self.frameDataQueue)
        if length==0:
            return True
        if frameData==self.frameDataQueue[length-1]:
            return False
        return True

    def putDataIntoQueue(self,dataDict):
        if self.notSameFrame(dataDict):
            if len(self.frameDataQueue) < self.frameNum:
                self.frameDataQueue.append(dataDict)
            else:
                self.frameDataQueue.pop(0)  # drop the old frame
                self.frameDataQueue.append(dataDict)
                #print(dataDict['Olr'],dataDict['Ofb'])


    def getAveQueue(self,target,rang=None):
        sum=0
        length=len(self.frameDataQueue)
        if rang==None:
            for data in self.frameDataQueue:
                sum += data[target]
        else:
            length = min(length,rang)
            for index in range(0,length):
                sum+=self.frameDataQueue[index][target]
        return sum/length

    def getAveTail(self,target,rang=3):
        length=len(self.frameDataQueue)
        if length<rang:
            return 0
        ave=0
        for i in range(length-rang,length):
            ave+=self.frameDataQueue[i][target]
        return ave/rang

    def judgeQueue(self,target,riseORdown,fisrtThreshold,lastThreshold,gap=None,failuresMax=0,rang=10):
        failures=0
        maxlen=rang
        minTar=999
        maxTar=-999
        if len(self.frameDataQueue)!=self.frameNum:
            return False
        for index,data in enumerate(self.frameDataQueue):
            if index>=maxlen:
                break
            maxTar=maxTar if maxTar>=data[target] else data[target]
            minTar=minTar if minTar<=data[target] else data[target]
            if index==0:
                if riseORdown=='RISE' and fisrtThreshold!=None:
                    if data[target]>fisrtThreshold:
                        return False
                if riseORdown=='DOWN' and fisrtThreshold!=None:
                    if data[target]<fisrtThreshold:
                        return False
            if index==(self.frameNum-1):
                if riseORdown=='RISE' and lastThreshold!=None:
                    if data[target]<lastThreshold:
                        return False
                if riseORdown=='DOWN' and lastThreshold!=None:
                    if data[target]>lastThreshold:
                        return False

            if index!=0:
                if riseORdown=='RISE' and data[target]<self.frameDataQueue[index-1][target]:
                    failures += 1
                if riseORdown=='DOWN' and data[target]>self.frameDataQueue[index-1][target]:
                    failures += 1

        if gap!=None:
            if (maxTar-minTar)<gap:
                return False
        if failures>failuresMax:
            return False
        return True

    def stop(self):
        self.mouse.stop()
        PressKey('esc')

    def __call__(self, skeletonData):
        #calculate Olr, Ofb, Oleft, Oright, Oshoulder, Oshoulder_hip, Dleg, Aspine
        #update lastSpineStatus
        #judge status of key and mouse in current frame
        frameData={
        'Olr':getAngle_skeletons_data(skeletonData,HeadShoulder_lr),
        'Ofb':getAngle_skeletons_data(skeletonData,HeadShoulder_fb),
        'Oleft':getAngle_skeletons_data(skeletonData,LeftHandElbow),
        'Oright':getAngle_skeletons_data(skeletonData,RightHandElbow),
        'Dview_lr':getDeltZ_skeletons_data_(skeletonData,LRshoulder),
        'Dview_ud':getDeltZ_skeletons_data_(skeletonData,UDshoulder),
        'Dleg':getDeltZ_skeletons_data(skeletonData,ShiftLeg),
        'accAlt':skeletonData.SkeletonPositions[JointId.ShoulderCenter].x,
        'accSpace':skeletonData.SkeletonPositions[JointId.ShoulderCenter].y,
        'leftOff':skeletonData.SkeletonPositions[JointId.HandLeft].y-skeletonData.SkeletonPositions[JointId.Head].y,
        'rightOff':skeletonData.SkeletonPositions[JointId.HandRight].y-skeletonData.SkeletonPositions[JointId.Head].y
        }
        if not self.isInit():
            self.setConfigInit(frameData)
            print('init ready')
            #print(skeletonData.SkeletonPositions[JointId.HandLeft])
            #print(skeletonData.SkeletonPositions[JointId.HandRight])
        self.putDataIntoQueue(frameData)

        #print(frameData['Ofb'],frameData['Olr'])

        # WASD
        if self.judgeQueue('Olr', 'DOWN', self.configInit['Olr'] - 6 / self.gestureSensitivity,
                           self.configInit['Olr'] - 12 / self.gestureSensitivity):
        #if self.frameDataQueue[-1]['Olr'] < (self.configInit['Olr'] - 15 / self.gestureSensitivity):
            if not self.KeyStatus['a']:
                ReleaseKey('d')
                ReleaseKey('w')
                ReleaseKey('s')
                PressKey('a')
                self.KeyStatus['a']=True
                print 'PressKey(a)'
        # if (125-Olr)<10:
        if self.judgeQueue('Olr', 'RISE', self.configInit['Olr'] - 12 / self.gestureSensitivity,
                           self.configInit['Olr'] - 6 / self.gestureSensitivity):
            # pass
            if self.KeyStatus['a']:
                ReleaseKey('a')
                ReleaseKey('d')
                ReleaseKey('w')
                ReleaseKey('s')
                self.KeyStatus['a']=False
                self.KeyStatus['d']=False
                self.KeyStatus['w']=False
                self.KeyStatus['s']=False
                print 'ReleaseKey(a)'
        #
        # if (Olr-125)>10:
        if self.judgeQueue('Olr', 'RISE', self.configInit['Olr'] + 6 / self.gestureSensitivity,
                           self.configInit['Olr'] + 12 / self.gestureSensitivity):
        # if self.frameDataQueue[-1]['Olr'] > (self.configInit['Olr'] + 15 / self.gestureSensitivity):
            if not self.KeyStatus['d']:
                ReleaseKey('a')
                ReleaseKey('w')
                ReleaseKey('s')
                PressKey('d')
                self.KeyStatus['d']=True
                print 'PressKey(d)'
        # # if (Olr-125)<10:
        if self.judgeQueue('Olr', 'DOWN', self.configInit['Olr'] + 12 / self.gestureSensitivity,
                           self.configInit['Olr'] + 6 / self.gestureSensitivity):
            #     #pass
            if self.KeyStatus['d']:
                ReleaseKey('a')
                ReleaseKey('d')
                ReleaseKey('w')
                ReleaseKey('s')
                self.KeyStatus['a'] = False
                self.KeyStatus['d'] = False
                self.KeyStatus['w'] = False
                self.KeyStatus['s'] = False
                print 'ReleaseKey(d)'
        #
        # if (155-Ofb)>10:
        if self.judgeQueue('Ofb', 'DOWN', self.configInit['Ofb'] - 5 / self.gestureSensitivity,
                           self.configInit['Ofb'] - 15 / self.gestureSensitivity):
        # if self.frameDataQueue[-1]['Ofb'] < (self.configInit['Ofb'] - 19 / self.gestureSensitivity):
            if not self.KeyStatus['w']:
                ReleaseKey('d')
                ReleaseKey('a')
                ReleaseKey('s')
                PressKey('w')
                self.KeyStatus['w']=True
                print 'PressKey(w)'
        # # if (155-Ofb)<10:
        if self.judgeQueue('Ofb', 'RISE', self.configInit['Ofb'] - 15 / self.gestureSensitivity,
                           self.configInit['Ofb'] - 5 / self.gestureSensitivity):
            #     #pass
            if self.KeyStatus['w']:
                ReleaseKey('a')
                ReleaseKey('d')
                ReleaseKey('w')
                ReleaseKey('s')
                self.KeyStatus['a'] = False
                self.KeyStatus['d'] = False
                self.KeyStatus['w'] = False
                self.KeyStatus['s'] = False
                print 'ReleaseKey(w)'
        #
        # if (Ofb-155)>10:
        if self.judgeQueue('Ofb', 'RISE', self.configInit['Ofb'] + 2 / self.gestureSensitivity,
                           self.configInit['Ofb'] + 9 / self.gestureSensitivity):
        # if self.frameDataQueue[-1]['Ofb'] > (self.configInit['Ofb'] + 8 / self.gestureSensitivity):
            if not self.KeyStatus['s']:
                ReleaseKey('d')
                ReleaseKey('w')
                ReleaseKey('a')
                PressKey('s')
                self.KeyStatus['s']=True
                print 'PressKey(s)'
        # # if (Ofb-155)<10:
        if self.judgeQueue('Ofb', 'DOWN', self.configInit['Ofb'] + 9 / self.gestureSensitivity,
                           self.configInit['Ofb'] + 2 / self.gestureSensitivity):
            #     #pass
            if self.KeyStatus['s']:
                ReleaseKey('a')
                ReleaseKey('d')
                ReleaseKey('w')
                ReleaseKey('s')
                self.KeyStatus['a'] = False
                self.KeyStatus['d'] = False
                self.KeyStatus['w'] = False
                self.KeyStatus['s'] = False
                print 'ReleaseKey(s)'
        # #SHIFT
        # if Dleg!=0:
        if self.judgeQueue('Dleg', 'RISE', self.configInit['Dleg'] + 0.01, self.configInit['Dleg'] + 0.06,failuresMax=7):
            if not self.KeyStatus['shift']:
                PressKey('lshift')
                self.KeyStatus['shift']=True
                print 'press lshift'
        if self.judgeQueue('Dleg', 'DOWN', self.configInit['Dleg'] + 0.06, self.configInit['Dleg'] + 0.01,failuresMax=7):
            if self.KeyStatus['shift']:
                ReleaseKey('lshift')
                self.KeyStatus['shift']=False
                print 'release lshift'
        # #ALT

        # if AccAlt>0.3:
        if self.judgeQueue('accAlt', 'RISE', None, None, gap=0.12/self.gestureSensitivity,rang=3,failuresMax=2):
            tapKey('lalt',1)
            print 'tap lalt'

        # #SPACE
        # print AccSpace
        # if AccSpace>0.3:
        if self.judgeQueue('accSpace', 'RISE', None, None,gap=0.12/self.gestureSensitivity ,rang=3,failuresMax=2):
            tapKey('space',1)
            print 'tap space'

        #Sword 1, Sword2, Game over
        sw1_on=self.judgeQueue('leftOff','RISE',0,0.2)
        sw1_off=self.judgeQueue('leftOff','DOWN',0.2,0)
        sw2_on=self.judgeQueue('rightOff','RISE',0,0.2)
        sw2_off=self.judgeQueue('rightOff','DOWN',0.2,0)

        if sw1_on and not sw2_on:
            PressKey('1')
            print('1')

        if sw1_off and not sw2_off:
            ReleaseKey('1')

        if sw2_on and not sw1_on:
            PressKey('2')
            print('2')

        if sw2_off and not sw1_off:
            ReleaseKey('2')

        if sw1_on and sw2_on:
            print('''-------------------------------
                    ---------------Game Over------------
                    ------------------------------------''')

            self.stop()
            os._exit(0)
            return False

        # #MOUSE
        # view
        self.mouse.move(int(-self.getAveQueue('Dview_lr', rang=2) * MOUSESENSITY),
                        int(-self.getAveQueue('Dview_ud', rang=2) * 0.1*MOUSESENSITY))
        # print self.getAveQueue('Dview_lr')*MOUSESENSITY,self.getAveQueue('Dview_ud')*MOUSESENSITY
        # #left
        # print Oleft
        judgeLeftPress = self.judgeQueue('Oleft', 'DOWN', self.configInit['Oleft'] - 10 / self.gestureSensitivity,
                                         self.configInit['Oleft'] - 80 / self.gestureSensitivity,failuresMax=3)
        judgeLeftRelease = self.judgeQueue('Oleft', 'RISE', self.configInit['Oleft'] - 80 / self.gestureSensitivity,
                                           self.configInit['Oleft'] - 10 / self.gestureSensitivity,failuresMax=3)
        judgeRightPress = self.judgeQueue('Oright', 'DOWN',
                                          self.configInit['Oright'] - 10 / self.gestureSensitivity,
                                          self.configInit['Oright'] - 80 / self.gestureSensitivity,failuresMax=3)
        judgeRightRelease = self.judgeQueue('Oright', 'RISE',
                                            self.configInit['Oright'] - 80 / self.gestureSensitivity,
                                            self.configInit['Oright'] - 10 / self.gestureSensitivity,failuresMax=3)
        # print judgeLeftPress,judgeLeftRelease,judgeRightPress,judgeRightRelease

        # if (170-Oleft)>30:
        if judgeLeftPress and not judgeRightPress:
            if not self.KeyStatus['left']:
                self.mouse.press(lmr=1)
                self.KeyStatus['left']=True
                print 'left press'
        # else:
        if judgeLeftRelease and not judgeRightRelease:
            if self.KeyStatus['left']:
                self.mouse.release(lmr=1)
                self.KeyStatus['left']=False
                print 'left release'

        # # #right
        # if(170-Oright)>30:
        if judgeRightPress and not judgeLeftPress:
            if not self.KeyStatus['right']:
                self.mouse.press(lmr=2)
                self.KeyStatus['right']=True
                print 'right press'
        # else:
        if judgeRightRelease and not judgeLeftRelease:
            if self.KeyStatus['right']:
                self.mouse.release(lmr=2)
                self.KeyStatus['right']=False
                print 'right release'

        '''
        # #middle
        if judgeLeftPress and judgeRightPress and :
        # if not (not ((170 - Oleft) > 10) or not ((170 - Oleft) < 90) or not ((170- Oright) > 10) or not (
        #         (170 - Oright) < 90) or not (abs(Oleft - Oright) < 5)):
        # if((170 - Oleft)>20and(170- Oright) >20 and (170- Oright) <90and (170 - Oleft)<90):
            self.mouse.press(lmr=3)
            print 'middle press'
        # else:
        if judgeLeftRelease and judgeRightRelease:
            self.mouse.release(lmr=3)
            print 'middle release'
        '''
        # #Q
        '''
        # if (180-Oleft)>90 and (180-Oright)>90:
        if self.judgeQueue('Oleft', 'DOWN', self.configInit['Oleft'] - 10 / self.gestureSensitivity,
                           self.configInit['Oleft'] - 90 / self.gestureSensitivity) and \
                self.judgeQueue('Oright', 'DOWN', self.configInit['Oright'] - 10 / self.gestureSensitivity,
                                self.configInit['Oright'] - 90 / self.gestureSensitivity):
            #     #PressKey('q')
            print 'press q'
        if self.judgeQueue('Oleft', 'RISE', self.configInit['Oleft'] - 80 / self.gestureSensitivity,
                           self.configInit['Oleft'] - 15 / self.gestureSensitivity) and \
                self.judgeQueue('Oright', 'RISE', self.configInit['Oright'] - 80 / self.gestureSensitivity,
                                self.configInit['Oright'] - 15 / self.gestureSensitivity):
            # else:
            #     #ReleaseKey('q')
            print 'release q'
        '''

        if judgeLeftPress and judgeRightPress:
            if not self.KeyStatus['q']:
                PressKey('q')
                self.KeyStatus['q']=True
                print 'Press q'
            # else:
        if judgeLeftRelease and judgeRightRelease:
            if self.KeyStatus['q']:
                ReleaseKey('q')
                self.KeyStatus['q']=False
                print 'release q'
        return True


