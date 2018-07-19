Kinect controller for witcher3

code in python
Author: Li+*

Witcher3 is the best game I played in my school life, and when teacher asked us to use kinect1 to do something I choose to write
a controller for Witcher games without delay. To be honest the final version doesn't meet my original idea, the WASDs are not sensitive
and sometimes space and alt will repeat several times when you press them. Maybe I would choose not to use the angle but relative locations to control if I could rewrite this project. But I don't have enough time ,I need to face my GRE first.

Though there still be some thing useful for every visitor. I overcame the difficulty in mouse and keyboard control in games by using ctypes.win32 API and user32.SetWindowsHookExA. Thanks to the help from this answer from stack overflow:
https://stackoverflow.com/questions/31379169/setting-up-a-windowshook-in-python-ctypes-windows-api





runtime environment£º
python2.7 32bit
windows10

how to run:
1.pip install -r requirements.txt
2.python main.py
