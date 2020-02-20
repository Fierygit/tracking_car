# -*- coding: utf-8 -*-
"""
Created on Sat May  4 14:02:25 2019

@author: tony_xc
"""

import cv2
import sys
import glob
import time

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
#print(major_ver, minor_ver, subminor_ver) # windows 3.4.5

def getTracker(tracker_type):  #选择类型
    if tracker_type == 'BOOSTING':
        tracker = cv2.TrackerBoosting_create()
    if tracker_type == 'MIL':
        tracker = cv2.TrackerMIL_create()
    if tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    if tracker_type == 'TLD':
        tracker = cv2.TrackerTLD_create()
    if tracker_type == 'MEDIANFLOW':
        tracker = cv2.TrackerMedianFlow_create()
    if tracker_type == 'GOTURN':
        tracker = cv2.TrackerGOTURN_create()
    if tracker_type == 'MOSSE':
        tracker = cv2.TrackerMOSSE_create()
    if tracker_type == "CSRT":
        tracker = cv2.TrackerCSRT_create()

    return tracker

if __name__ == '__main__':

    # Set up tracker.
    # Instead of MIL, you can also use

    tracker_types = {0:'BOOSTING', 1:'MIL', 2:'KCF', 3:'TLD',
                     4:'MEDIANFLOW', 5:'GOTURN', 6:'MOSSE', 7:'CSRT'}
    tracker_type = tracker_types[2]

    if (int(minor_ver)<3 and int(major_ver)<3 ):
        tracker = cv2.Tracker_create(tracker_type)
    else:
        tracker = getTracker(tracker_type)
    picNum = 0
    failureNum = 0
    # Read jpg
    for i in range(1,150):
    #for jpgfile in glob.glob(r'E:\Semester_three_up\strawberry_pie\opencv-tracking\picture\*.jpg'):
        
        jpgfile = str("E:\Semester_three_up\\strawberry_pie\\opencv-tracking\picture\\" + str(i) + '.jpg')
        print(jpgfile)
        frame = cv2.imread(jpgfile,cv2.IMREAD_ANYCOLOR)
        picNum = picNum + 1
        if picNum == 1 :
            bbox = cv2.selectROI(frame, False)   
            ok = tracker.init(frame, bbox)
        else:
            # Start timer
            #timer = cv2.getTickCount()

            # Update tracker
            ok, bbox = tracker.update(frame)

            # Calculate Frames per second (FPS)
            #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
            # Draw bounding box
            if ok:
                # Tracking success
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            else:
                # Tracking failure
                cv2.putText(frame, "Tracking failure detected", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                failureNum = failureNum + 1

            # Display tracker type on frame
            cv2.putText(frame, tracker_type + " Tracker", (50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);

            # Display FPS on frame
            # cv2.putText(frame, "FPS : " + str(int(fps)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);

            # Display result
            cv2.imshow("Tracking", frame)

            # Exit if ESC pressed
            k = cv2.waitKey(10) & 0xff
            if k == 27: break
            
    time.sleep(1)
    print(picNum)
    print(failureNum)
    cv2.destroyAllWindows() # close windows
