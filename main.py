#In this file I will achieve read data from kinect and use functions in sk2key.py to output right keys.

import thread
import itertools
import ctypes
import logging
import Queue
import threading

import time

import pykinect
from pykinect import nui
from pykinect.nui import JointId

import pygame
from pygame.color import THECOLORS
from pygame.locals import *

from sk2key import *
from tools import *

KINECTEVENT = pygame.USEREVENT
DEPTH_WINSIZE = 320, 240
VIDEO_WINSIZE = 640, 480
# main game loop
done = False
_task_queue = Queue.Queue()

mouseController=MouseController()
gestureController=GestureController(mouseController)

def async_call(skeletonData):
    _task_queue.put({
        'data': skeletonData
    })
def _task_queue_consumer():
    while True:
        try:
            task = _task_queue.get()
            data=task.get('data')
            try:
                if data:
                    if not gestureController(data):
                        done=True
            except Exception as ex:
                if data:
                    import traceback
                    traceback.print_exc()
                    break
            finally:
                _task_queue.task_done()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            break

def handle_result(result):
    #print(result)
    pass

pygame.init()

skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image


def draw_skeleton_data(pSkelton, inde, positions, width=4):
    start = pSkelton.SkeletonPositions[positions[0]]

    for position in itertools.islice(positions, 1, None):
        next = pSkelton.SkeletonPositions[position.value]

        curstart = skeleton_to_depth_image(start, dispInfo.current_w, dispInfo.current_h)
        curend = skeleton_to_depth_image(next, dispInfo.current_w, dispInfo.current_h)

        pygame.draw.line(screen, SKELETON_COLORS[inde], curstart, curend, width)

        start = next


# recipe to get address of surface: http://archives.seul.org/pygame/users/Apr-2008/msg00218.html
if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
    Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
    Py_ssize_t = ctypes.c_int64
else:
    raise TypeError("Cannot determine type of Py_ssize_t")

_PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
_PyObject_AsWriteBuffer.restype = ctypes.c_int
_PyObject_AsWriteBuffer.argtypes = [ctypes.py_object,
                                    ctypes.POINTER(ctypes.c_void_p),
                                    ctypes.POINTER(Py_ssize_t)]


def surface_to_array(surface):
    buffer_interface = surface.get_buffer()
    address = ctypes.c_void_p()
    size = Py_ssize_t()
    _PyObject_AsWriteBuffer(buffer_interface,
                            ctypes.byref(address), ctypes.byref(size))
    bytes = (ctypes.c_byte * size.value).from_address(address.value)
    bytes.object = buffer_interface
    return bytes


def draw_skeletons(skeletons):
    index=0
    while (index <= 5 and skeletons[index].SkeletonPositions[JointId.Head].x == 0
           and skeletons[index].SkeletonPositions[JointId.Head].y == 0
           and skeletons[index].SkeletonPositions[JointId.Head].z == 0):
        index += 1

    if index<=5:
        data = skeletons[index]
        async_call(data)
        # draw the Head
        '''
        if index==0:
            print(data.SkeletonPositions[JointId.Head])
        '''
        HeadPos = skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], dispInfo.current_w, dispInfo.current_h)
        draw_skeleton_data(data, index, SPINE, 10)
        pygame.draw.circle(screen, SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)
        '''
        if int(HeadPos[0])!=0 and int(HeadPos[1])!=0:
            print index
        '''
        # drawing the limbs
        draw_skeleton_data(data, index, LEFT_ARM)
        draw_skeleton_data(data, index, RIGHT_ARM)
        draw_skeleton_data(data, index, LEFT_LEG)
        draw_skeleton_data(data, index, RIGHT_LEG)



def depth_frame_ready(frame):
    if video_display:
        return

    with screen_lock:
        address = surface_to_array(screen)
        frame.image.copy_bits(address)
        del address
        if skeletons is not None and draw_skeleton:
            draw_skeletons(skeletons)
        pygame.display.update()


def video_frame_ready(frame):
    if not video_display:
        return

    with screen_lock:
        address = surface_to_array(screen)
        frame.image.copy_bits(address)
        del address
        if skeletons is not None and draw_skeleton:
            draw_skeletons(skeletons)
        pygame.display.update()


if __name__ == '__main__':
    full_screen = False
    draw_skeleton = True
    video_display = False
    dataPipe=threading.Thread(target=_task_queue_consumer)
    dataPipe.daemon = True
    dataPipe.start()
    screen_lock = thread.allocate()
    screen = pygame.display.set_mode(DEPTH_WINSIZE, 0, 16)
    pygame.display.set_caption('Python Kinect Demo')
    skeletons = None
    screen.fill(THECOLORS["black"])
    kinect = nui.Runtime()
    kinect.skeleton_engine.enabled = True


    def post_frame(frame):
        try:
            pygame.event.post(pygame.event.Event(KINECTEVENT, skeletons=frame.SkeletonData))
        except:
            # event queue full
            pass


    kinect.skeleton_frame_ready += post_frame

    kinect.depth_frame_ready += depth_frame_ready
    kinect.video_frame_ready += video_frame_ready

    kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
    kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)

    print('Controls: ')
    print('     d - Switch to depth view')
    print('     v - Switch to video view')
    print('     s - Toggle displaing of the skeleton')
    print('     u - Increase elevation angle')
    print('     j - Decrease elevation angle')



    print('Please stand relaxedly in front of kinect and let your whole skeletons displayed on the screen correctly' )
    print('Before start, it will delay 5 secs')
    time.sleep(5)

    while not done:
        e = pygame.event.wait()
        dispInfo = pygame.display.Info()
        if e.type == pygame.QUIT:
            done = True
            gestureController.stop()
            break
        elif e.type == KINECTEVENT:
            skeletons = e.skeletons

            if draw_skeleton:
                draw_skeletons(skeletons)
                pygame.display.update()
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                gestureController.stop()
                done = True
                break
            elif e.key == K_d:
                with screen_lock:
                    screen = pygame.display.set_mode(DEPTH_WINSIZE, 0, 16)
                    video_display = False
            elif e.key == K_v:
                with screen_lock:
                    screen = pygame.display.set_mode(VIDEO_WINSIZE, 0, 32)
                    video_display = True
            elif e.key == K_s:
                draw_skeleton = not draw_skeleton
            elif e.key == K_u:
                kinect.camera.elevation_angle = kinect.camera.elevation_angle + 2
            elif e.key == K_j:
                kinect.camera.elevation_angle = kinect.camera.elevation_angle - 2
            elif e.key == K_x:
                kinect.camera.elevation_angle = 2
