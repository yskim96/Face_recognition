'''
Human temperature, Face Detect and Reconigtion with Azure Face API
writen by ys
last modify 2021/06/21 

TODO : Thermal sensor Require Calibation 
You have to take a heat source with same defined temperature over all pixels of
GridEYE. Then you have to measure and to calculate the Offset to this defined temperature for
every pixel. Then you can add or subtract this Offset to the corresponding pixel temperature
value in your μController algorithm.

For Example:
Defined temperature over all pixels: 30° C
Pixel 1 value: 29,5 ° C _ Offset: -0,5° C _ Add in algorithm 0,5° C to value of pixel 1
Pixel 2 value: 30,25 ° C _ Offset: +0,25° C _ Subtract in algorithm 0,25° C to value of pixel 2
'''

import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person

import threading
from queue import Queue

from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from itertools import count, cycle

from picamera import PiCamera
from picamera.array import PiRGBArray
from Adafruit_AMG88xx import Adafruit_AMG88xx
import cv2
import numpy as np
from time import sleep
import time

import config

KEY = config.api_key
ENDPOINT = config.endpoint

# Create an authenticated FaceClient.
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

root = Tk()
# jipmusil ident color
root.configure(background='#222F40')
root.attributes('-zoomed', True)
# raspberry pi 7 inch touchscreen resolution
root.geometry("480x800")

myCanvas = Canvas(root)
myCanvas.config(width=480, height=800, background='#222F40')
myCanvas.pack()

camera = PiCamera()
camera.resolution = (480, 800)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(480, 800))

sensor = Adafruit_AMG88xx(00, 0x69, None)
thermal_cal = 10.5

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eyesCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

time.sleep(0.1)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        
def create_circle(x, y, r, w, line_color, canvasName): #center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r 
    y1 = y + r - 20
    return canvasName.create_oval(x0, y0, x1, y1, width=w, outline=line_color )

def k(arg, q):
    global root
    global verify_tick
    global lbl
    verify_tick = 0
    chk = 1
    #l = Label(root)
    #l.pack()

    face_icon = PhotoImage(file='images/faceid.png')
    myCanvas.create_image(140, 130, image=face_icon, anchor=NW)
    f_tempLabel = myCanvas.create_text(240, 335, text="", fill='white', font=('Helvetica',28))
    f_textAdviser = myCanvas.create_text(240, 500, text="", fill='white', font=('Helvetica',32))
    f_backcircle = create_circle(240, 240, 160, 20, 'gray', myCanvas)
    f_circle = create_circle(240, 240, 160, 5, 'white', myCanvas)
    

    while chk:
        data, evt = q.get()
        print('Receive Original Data : {}'.format(data))
        evt.set()
        #myCanvas.delete("all")
        q.task_done()        
        
        # face Detect
        if data[0] == 1:
            
            pixels = sensor.readPixels()
            cal_pix = np.array(pixels) + thermal_cal
        # adaptive min and max temperature colour visualization
            MINTEMP = min(cal_pix)
            MAXTEMP = max(cal_pix)
            myCanvas.itemconfig(f_tempLabel, text=MAXTEMP)
            myCanvas.itemconfig(f_textAdviser, text='Face Deteted')
            
            if data[2] <= 290:
                f_sizePerdotSpace = map(data[2],150,250,18,5)
                f_sizePerLineWidth = map(data[2],150,250,5,18)
                myCanvas.itemconfig(f_circle, outline='white')
                myCanvas.itemconfig(f_circle, width=abs(f_sizePerLineWidth), dash=(3,round(abs(f_sizePerdotSpace))))
                
            else:
                myCanvas.itemconfig(f_textAdviser, text='Too Close')
                
            if data[2] >= 200:
                f_verifyIconFill = map(verify_tick,0,5,1,50)
                myCanvas.itemconfig(f_backcircle, outline='white', outlineoffset='center', width=f_verifyIconFill)
                #print(verify_tick)
                verify_tick = verify_tick + 1
                
            if verify_tick >= 5:
                myCanvas.itemconfig(f_backcircle, outline='white', fill='white')
                myCanvas.itemconfig(f_textAdviser, text='Verifying...')

                chk = face_Recognition(data[4])
                print(chk)
        else:
            verify_tick = 0
            myCanvas.itemconfig(f_circle, outline='gray')
            myCanvas.itemconfig(f_backcircle, outline='gray', outlineoffset='center', width=20)
            myCanvas.itemconfig(f_textAdviser, text='Look at front')
        
        #print("face axis {}".format(data))
    
    #def submit():
        #l.configure(text = e.get())
    #Button(text="Submit",command=submit).pack()

def face_Recognition(request_img):
    print("face Recognition requset")
    
    # TODO: image transfer without file save (binary stream)
    img = Image.fromarray(request_img)
    img.save('face_buf.png', format='PNG')
    time.sleep(0.01)
    v = open('face_buf.png', 'r+b')

    detected_faces = face_client.face.detect_with_stream(v, detection_model='detection_03')
    if not detected_faces:
        raise Exception('No face detected from image {}'.format(v))

    # Save this ID for use in Find Similar
    image_face_ID = detected_faces[0].face_id
    print(image_face_ID)
    
    # TODO: not yet develop enduser face add dialog just hardcoding face id(me)
    verify_result_same = face_client.face.verify_face_to_face('104f2e4d-3a38-4e32-8075-7d8219081385', image_face_ID)
    if verify_result_same.is_identical:
        print('Faces the same person, with confidence: {}'.format(verify_result_same.confidence))
        v_circle = create_circle(240, 240, 160, 5, 'white', myCanvas)
        
        for i in range(5,1000,1*2):
            myCanvas.itemconfig(v_circle, width=i, outline='#FDF6EE', fill='#FDF6EE')
            f_textAdviser = myCanvas.create_text(235, 400, text="Hello!", fill='black', font=('Helvetica',65))
        
        return 0
    
        while True:
            print("")
            #lbl.load('images/darkbear.gif')
 
    else:
        print('Faces a different person, with confidence: {}'.format(verify_result_same.confidence))
        data[0] = 0
        verify_tick = 0
        return 1

    
def threaded_function(arg, data, q):
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(50, 50))

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = image[y:y + h, x:x + w]
            eyes = eyesCascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                #print(eyes)
                cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (100, 255, 255), 2)
            # Azure Recommend : face size 200px x 200px, eye for eye 100px
            #if (w-x) >= 200 or (h-y) >= 200:
                #print("ideal face size")                        
                
            if len(faces) >= 1 and len(eyes) >= 2:
                #cv2.putText(image, 'WARNING!', (10, 500), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 2)
                print("Great")
                # eyes detect
                data[1] = 1
                data[2] = (w)
                data[3] = (h)
                data[4] = gray
                
            elif len(eyes) >= 0:
                print("Look at the Front")
                # face detect
                data[0] = 1
                # face box size x,y
                data[2] = (w)
                data[3] = (h)
                # eye detect
                data[1] = 0
                # To-Do : left or right detect, compare eyes array each x, y
        
        if len(faces) <= 0:
            # no face
            data[0] = 0
            #break
            print("No Detected face")
        
        evt = threading.Event()
        q.put((data, evt))
        evt.wait()
            
        #cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        
            
            
        if key == ord("q"):
            break
    cv2.destroyAllWindows()
        
if __name__ == "__main__":
    q = Queue()
    # face detect, eye count, facebox x, y
    global data
    data = [0,0,0,0,0]
    thread = threading.Thread(target = threaded_function, args = (12, data, q))
    thread2 = threading.Thread(target = k, args = (12, q))
    thread.start()
    thread2.start()
    print(data)
    q.join()
    
    root.mainloop()
