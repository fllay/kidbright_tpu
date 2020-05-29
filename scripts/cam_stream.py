#!/usr/bin/env python
import numpy as np
import cv2
import rospy
from picamera.array import PiRGBArray
from picamera import PiCamera
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage

def camThread():

    width = 640
    height = 480
    #vidfps = 30

    cam = cv2.VideoCapture(0)
    cam.set(3,width)
    cam.set(4,height)
    cam.set(cv2.CAP_PROP_FPS,15)
    #cam = cv2.VideoCapture(get_camerasrc(0), cv2.CAP_GSTREAMER)

    #cam.set(cv2.CAP_PROP_FPS, vidfps)
    #cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    #cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    #cam = cv2.VideoCapture('rkisp device=/dev/video1 io-mode=4 path-iqf=/etc/cam_iq/ov13850.xml ! video/x-raw,format=NV12,width=740 ,height=360,framerate=30/1 ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
    image_pub = rospy.Publisher("/output/image_raw/compressed", CompressedImage, queue_size=1)
    rospy.init_node('cam_stream', anonymous=True)
    rate = rospy.Rate(30) # 10hz

    while not rospy.is_shutdown():
        try:
            ret, color_image = cam.read()
            if not ret:
                print("no image")
                continue
            msg = CompressedImage()
            msg.header.stamp = rospy.Time.now()
            msg.format = "jpeg"
            msg.data = np.array(cv2.imencode('.jpg', color_image)[1]).tostring()
            # Publish new image
            image_pub.publish(msg)

            res = None
        except BaseException as e: 
            print("Exiting")
            print(e)
        except (KeyboardInterrupt, SystemExit):
            print("Camera release")
            cam.release() 
            break
        
        rate.sleep()

def camCap():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))
    image_pub = rospy.Publisher("/output/image_raw/compressed", CompressedImage, queue_size=10)
    rospy.init_node('cam_stream', anonymous=True)
    rate = rospy.Rate(30) # 10hz
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):        
        try:
            image = frame.array
            msg = CompressedImage()
            msg.header.stamp = rospy.Time.now()
            msg.format = "jpeg"
            msg.data = np.array(cv2.imencode('.jpg', image)[1]).tostring()
            # Publish new image
            image_pub.publish(msg)

            res = None
        except BaseException as e: 
            print(e)
            print("Exiting")
            camera.close()
            break
            
        except (KeyboardInterrupt, SystemExit):
            print("Camera release")
            camera.close()
            break

        res = None
        rawCapture.truncate(0)
        rate.sleep()


if __name__ == '__main__':
    #cam = cv2.VideoCapture(0)
    #cam.set(5 , 30) 

    try:
        camThread()
        #camCap()
    except rospy.ROSInterruptException:
        pass
