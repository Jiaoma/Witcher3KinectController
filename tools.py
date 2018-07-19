import numpy as np

import pykinect
from pykinect import nui
from pykinect.nui import JointId

from pygame.color import THECOLORS

LEFT_ARM = (JointId.ShoulderCenter,
            JointId.ShoulderLeft,
            JointId.ElbowLeft,
            JointId.WristLeft,
            JointId.HandLeft)
RIGHT_ARM = (JointId.ShoulderCenter,
             JointId.ShoulderRight,
             JointId.ElbowRight,
             JointId.WristRight,
             JointId.HandRight)
LEFT_LEG = (JointId.HipCenter,
            JointId.HipLeft,
            JointId.KneeLeft,
            JointId.AnkleLeft,
            JointId.FootLeft)
RIGHT_LEG = (JointId.HipCenter,
             JointId.HipRight,
             JointId.KneeRight,
             JointId.AnkleRight,
             JointId.FootRight)
SPINE = (JointId.HipCenter,
         JointId.Spine,
         JointId.ShoulderCenter,
         JointId.Head)

SKELETON_COLORS = [THECOLORS["red"],
                   THECOLORS["blue"],
                   THECOLORS["green"],
                   THECOLORS["orange"],
                   THECOLORS["purple"],
                   THECOLORS["yellow"],
                   THECOLORS["violet"]]



def getAngle(Pa,Pb,Pc):

    ba = Pa - Pb
    bc = Pc - Pb

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

def getDeltZ(za,zb):
    '''
    if (za-zb)>threshold:
        return -1
    elif (zb-za)>threshold:
        return 1
    else:
        return 0
    '''
    return abs(za-zb)


def getAngle_skeletons_data(data,positions):
    a=data.SkeletonPositions[positions[0]]
    b = data.SkeletonPositions[positions[1]]
    c = data.SkeletonPositions[positions[2]]
    return getAngle(np.array([a.x,a.y,a.z]),np.array([b.x,b.y,b.z]),np.array([c.x,c.y,c.z]))

def getDeltZ_skeletons_data(data,positions):
    return getDeltZ(data.SkeletonPositions[positions[0]].z,data.SkeletonPositions[positions[1]].z)

def getDeltZ_skeletons_data_(data,positions):
    return data.SkeletonPositions[positions[0]].z-data.SkeletonPositions[positions[1]].z

def getAccSpeed(last,current,direction=0,ignore=False):
    lastVector=np.array([last.x,last.y,last.z])
    curVector=np.array([current.x,current.y,current.z])
    if ignore:
        return np.abs(np.max(0,lastVector[direction]-curVector[direction]))
    return np.abs(lastVector[direction]-curVector[direction])

if __name__=='__main__':
    a=np.array([1,np.sqrt(3),0])
    b=np.array([0,0,0])
    c=np.array([1,0,0])

    print(getAngle(a,b,c))