import cv2
from picamera2 import Picamera2
import timeit
from gpiozero import Motor
from time import sleep
import numpy

ENA = 12
IN1 = 15
IN2 = 14
IN3 = 22
IN4 = 27
ENB = 13

motor1 = Motor(forward=IN1, backward=IN2, enable=ENA) # CH1
motor2 = Motor(forward=IN3, backward=IN4, enable=ENB) # CH2

global glox

def yello_detect(img_src):
    img_hsv = cv2.cvtColor(img_src, cv2.COLOR_BGR2HSV)
    # img_h, img_s, img_v = cv2.split(img_hsv)

    yellow_mask = cv2.inRange(img_hsv, (25,0,0), (45,255,255))
    # img_yellow=cv2.bitwise_and(img_hsv, img_hsv, mask=yellow_mask)



    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    contours, hierarchy = cv2.findContours(yellow_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    x = 0; y = 0
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 1000:
            cv2.drawContours(img_src, [contour],0,(0,0,255),1)
            mu = cv2.moments(contour)
            cX = int(mu['m10'] / (mu['m00'] + 1e-5 ))
            cY = int(mu['m01'] / (mu['m00'] + 1e-5 ))
            x = cX
            y = cY
            # cv2.circle(img_src, (cX, cY), 5, (0,0,255), -1)
            # cv2.putText(img_src,f'{area}',(cX,cY+20),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),1)

    return img_src, x, y

# def red_detect():

# def green_detect():

# def color_detect():


picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format":'XRGB8888', "size": (800, 600)}))
picam2.start()

# avg_x = 0; avg_y = 0
listx = []

while True:    
    frame = picam2.capture_array()
    frame = cv2.pyrDown(frame)
    frame = cv2.flip(frame, -1)
    height, width = frame.shape[:2]

    frame_cut = frame[3*height//7:6*height//7, 0:width]
    frame_cut,x,y = yello_detect(frame_cut)

    if x > 0:
            # print("append")
            listx.append(x)
            # print(len(listx))

            if len(listx) == 5:
                # print("full")
                avg_x = sum(listx) / len(listx)

                # print(f"{avg_x} ----- ")
                listx = []

                if avg_x > 0:
                    if avg_x >= width//5 and avg_x <= 4*width//5:
                        motor1.forward(0.7)
                        motor2.forward(0.6)
                        print(avg_x)
                        print("forward")
                    if avg_x < width//5:
                        motor1.backward(0.6)
                        motor2.forward(0.6)  
                        print(avg_x)
                        print("left") 
                        # if x == 0:
                        #     print("leftback")
                        #     motor1.backward(0.4)
                    if avg_x > 4*width//5:
                        motor1.forward(0.6)
                        motor2.backward(0.6)
                        print("right")
                        # if x == 0:
                        #     print("rightback")
                        #     motor2.backward(0.4)
    elif x == 0:
        print("stop")
        motor1.backward(0.45)
        motor2.backward(0.45)