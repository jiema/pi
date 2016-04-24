#!/usr/bin/env python3
import sys, os
from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes
from datetime import datetime
import csv
import threading
import time
import ibmiotf.device

options = {
    "org": "q05eir",
    "type": "sensor",
    "id": "1d0b91e70599644cb1a3ca1657e16507",
    "auth-method": "token",
    "auth-token": "fg2KDQwyLSCO"
}
client = ibmiotf.device.Client(options)
client.connect()

dirstr = "/home/pi/data/sensehat/"
sense = SenseHat()
sense.clear()
#### FIND JOY_STICK -- BEGIN
devices = [InputDevice(fn) for fn in list_devices()]
for dev in devices:
    if dev.name == 'Raspberry Pi Sense HAT Joystick':
        found = True;
        break

if not(found):
    print('Raspberry Pi Sense HAT Joystick not found. Aborting ...')
    sys.exit()
#### FIND JOY_STICK -- END




UP_PIXELS = [[3, 0], [4, 0]]
DOWN_PIXELS = [[3, 7], [4, 7]]
LEFT_PIXELS = [[0, 3], [0, 4]]
RIGHT_PIXELS = [[7, 3], [7, 4]]
CENTRE_PIXELS = [[3, 3], [4, 3], [3, 4], [4, 4]]
 
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
GREEN = [0, 255, 0]
RED = [255, 0, 0]
def set_pixels(pixels, col):
    for p in pixels:
        sense.set_pixel(p[0], p[1], col[0], col[1], col[2])

set_pixels(DOWN_PIXELS, GREEN)
is_recording = False
global writer 
def handle_code(code, colour):
    if code == ecodes.KEY_DOWN:
        set_pixels(DOWN_PIXELS, colour)
    elif code == ecodes.KEY_UP:
        set_pixels(UP_PIXELS, colour)
        if colour == BLACK:
            sense.clear()
            os.system("sudo shutdown -h now")
    elif code == ecodes.KEY_LEFT:
        set_pixels(LEFT_PIXELS, colour)
    elif code == ecodes.KEY_RIGHT:
        set_pixels(RIGHT_PIXELS, colour)
    elif code == ecodes.KEY_ENTER:
        sense.clear()
        set_pixels(CENTRE_PIXELS, colour)
        global is_recording
        if colour == BLACK:
            if not is_recording:
                sense.show_message("START", text_colour=[255, 255, 255], scroll_speed = 0.05);
                sense.set_imu_config(True, True, True)

                rt = threading.Thread( target=record, args = () )
                rt.start()
                is_recording = True
            else:
                sense.show_message("STOP", text_colour=[255, 255, 255], scroll_speed = 0.03)
                os._exit(1)

def key():
    try:
        for event in dev.read_loop():
             if event.type == ecodes.EV_KEY:
                if event.value == 1:  # key down
                    handle_code(event.code, WHITE)
                if event.value == 0:  # key up
                    handle_code(event.code, BLACK)
    except KeyboardInterrupt:
        sys.exit()

def record():
    global running
    running = True
    current_colour = RED

    while running:
        

        set_pixels(DOWN_PIXELS, current_colour)

        if current_colour == RED:
            current_colour = BLACK
        else:
            current_colour = RED
        o = sense.get_orientation_radians()
        pitch = o["pitch"]
        roll = o["roll"]
        yaw = o["yaw"]
        #pitch = round(pitch, 5)
        #roll = round(roll, 5)
        #yaw = round(yaw, 5)

        accraw = sense.get_accelerometer_raw()
        acc_x = accraw["x"]
        acc_y = accraw["y"]
        acc_z = accraw["z"]
        #acc_x = round(acc_x, 5)
        #acc_y = round(acc_y, 5)
        #acc_z = round(acc_z, 5)
        myData={'d' : { 'x' : acc_x, 'y' : acc_y, 'z' : acc_z}}
        client.publishEvent("data_raw", "json", myData)
    
try:
 
   kt = threading.Thread( target=key, args = () )
   kt.start()

except:
   print ("Error: unable to start thread")

