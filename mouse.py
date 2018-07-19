from pymouse import PyMouse
from MouseHook import *

import ctypes

class MouseController:
    def __init__(self):
        self.m=PyMouse()
        self.mouseHook=TranslateInjectedMouse()
        self.mouseHook.start()
        self.mouseHookEvent=user32.mouse_event
        self.WINSIZE=self.m.screen_size()
        self.x=long(self.WINSIZE[0]/2)
        self.y=long(self.WINSIZE[1]/2)

    def moveAndClick(self,dx=0,dy=0,lmr=1):
        assert (dx!=None and dy!=None)
        self.x = self.x + long(dx) \
            if (self.x + long(dx)) >= 0 and (self.x + long(dx)) <= self.WINSIZE[0] \
            else (long(self.WINSIZE[0]) if (self.x + long(dx)) > self.WINSIZE[0]
                  else 0L)

        self.y = self.y + long(dy) \
            if (self.y + long(dy)) >= 0 and (self.y + long(dy)) <= self.WINSIZE[1] \
            else (long(self.WINSIZE[1]) if (self.y + long(dy)) > self.WINSIZE[1]
                  else 0L)
        self.m.release(self.x,self.y,lmr)
        self.m.click(self.x, self.y, lmr)
        #print(self.x, self.y)
        return

    def move(self,dx,dy):
        '''
        assert dx!=None and dy!=None
        self.x = self.x + long(dx) \
            if (self.x + long(dx)) >= 0 and (self.x + long(dx)) <= self.WINSIZE[0] \
            else (long(self.WINSIZE[0]) if (self.x + long(dx)) > self.WINSIZE[0]
                  else 0L)

        self.y = self.y + long(dy) \
            if (self.y + long(dy)) >= 0 and (self.y + long(dy)) <= self.WINSIZE[1] \
            else (long(self.WINSIZE[1]) if (self.y + long(dy)) > self.WINSIZE[1]
                  else 0L)
        '''
        self.mouseHookEvent(MOUSEEVENTF_MOVE,dx,dy,0,0)
        return

    def press(self,dx=0,dy=0,lmr=1):
        assert (dx != None and dy != None)
        self.x = self.x + long(dx) \
            if (self.x + long(dx)) >= 0 and (self.x + long(dx)) <= self.WINSIZE[0] \
            else (long(self.WINSIZE[0]) if (self.x + long(dx)) > self.WINSIZE[0]
                  else 0L)

        self.y = self.y + long(dy) \
            if (self.y + long(dy)) >= 0 and (self.y + long(dy)) <= self.WINSIZE[1] \
            else (long(self.WINSIZE[1]) if (self.y + long(dy)) > self.WINSIZE[1]
                  else 0L)
        self.m.press(self.x,self.y,lmr)
        return
    def release(self,dx=0,dy=0,lmr=1):
        assert dx != None and dy != None
        self.x = self.x + long(dx) \
            if (self.x + long(dx)) >= 0 and (self.x + long(dx)) <= self.WINSIZE[0] \
            else (long(self.WINSIZE[0]) if (self.x + long(dx)) > self.WINSIZE[0]
                  else 0L)

        self.y = self.y + long(dy) \
            if (self.y + long(dy)) >= 0 and (self.y + long(dy)) <= self.WINSIZE[1] \
            else (long(self.WINSIZE[1]) if (self.y + long(dy)) > self.WINSIZE[1]
                  else 0L)
        self.m.release(self.x, self.y, lmr)
        return

    def stop(self):
        if self.mouseHook.is_alive():
            self.mouseHook.stop()
        else:
            pass


if __name__=='__main__':
    mu = MouseController()
    # mu.move(100,100)
    import time
    time.sleep(5)
    c=5
    while(c>0):
        print(c)
        time.sleep(5)
        mu.move(10,0)
        time.sleep(5)
        mu.move(-10,0)
        c-=1
