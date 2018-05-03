import cv2 
import numpy as np
import math
import os
from PIL import Image

"""Used method to detect face from this tutorial
https://docs.opencv.org/3.4.1/d7/d8b/tutorial_py_face_detection.html"""

# xml files describing our haar cascade classifiers
faceCascadeFilePath = "haarcascade_frontalface_default.xml"
# Build our cv2 Cascade Classifiers
faceCascade = cv2.CascadeClassifier(faceCascadeFilePath)

# Collect video input from first webcam on system
cap = cv2.VideoCapture(1)

recognizer = cv2.face.LBPHFaceRecognizer_create()

def returnFaces():
 
    while True:
        
        # Reads image
        ret, frame = cap.read()
        # Converts image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detects face in the captured frame
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        # If any faces detected, returns True
        for (x, y, w, h) in faces:
            return True
        return False

"""Followed this tutorial to detect hand and return number of fingers
https://www.quora.com/What-is-the-easiest-way-to-recognise-gestures-in-
OpenCV-using-Python"""

def returnFingers():
    
    try:
        while(cap.isOpened()):
            
            # Read images
            ret, img = cap.read()
            
            # Creates a small sub window in top right corner to look for hands
            cv2.rectangle(img, (300,300), (100,100), (0,255,0),0)
            crop_img = img[100:300, 100:300]
            
            # Converts image to grayscale
            gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
            
            # Applys a blur so difference in colors is easier to detect
            blurSize = (35, 35)
            blurred = cv2.GaussianBlur(gray, blurSize, 0)
            
            # Thresholds image using Otsu's Binarization method
            _, thresh1 = cv2.threshold(blurred, 127, 255,
                                    cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
                                    
            # show thresholded image
            cv2.imshow('Thresholded', thresh1)
                                    
            image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                    cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            
            # Finds the contour with max area
            cnt = max(contours, key = lambda x: cv2.contourArea(x))
        
            # create bounding rectangle around the contour (can skip below two lines)
            #x, y, w, h = cv2.boundingRect(cnt)
            #cv2.rectangle(crop_img, (x, y), (x+w, y+h), (0, 0, 255), 0)
        
            # Finds convex hull
            hull = cv2.convexHull(cnt)
        
            # Drawing contours
            drawing = np.zeros(crop_img.shape,np.uint8)
            cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
            cv2.drawContours(drawing, [hull], 0,(0, 0, 255), 0)
        
            # finding convex hull
            hull = cv2.convexHull(cnt, returnPoints=False)
        
            # finding convexity defects
            defects = cv2.convexityDefects(cnt, hull)
            count_defects = 0
            cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)
        
            # applying Cosine Rule to find angle for all defects (between fingers)
            # with angle > 90 degrees and ignore defects
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]
        
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])
        
                # find length of all sides of triangle
                a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
        
                # apply cosine rule here
                angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
        
                # ignore angles > 90 and highlight rest with red dots
                if angle <= 90:
                    count_defects += 1
                    cv2.circle(crop_img, far, 1, [0,0,255], -1)
                #dist = cv2.pointPolygonTest(cnt,far,True)
        
                # draw a line from start to end i.e. the convex points (finger tips)
                # (can skip this part)
                #cv2.line(crop_img,start, end, [0,255,0], 2)
                #cv2.circle(crop_img,far,5,[0,0,255],-1)
                    
            # Two fingers detected
            if count_defects == 1: 
                #print("Two fingers")
                return 2
            # Three fingers detected
            elif count_defects == 2:
                #print("Three fingers")
                return 3
            #Four fingers detected
            elif count_defects == 3:
                #print("Four fingers")
                return 4
            # Five fingers detected
            elif count_defects == 4:
                #print("Five fingers")
                return 5
            # Either one finger or nothing detected
            else:
                #print("Nothing")
                return 0 

    #Avoids crashing of program if it cannot detect any shapes            
    except Exception as e:
        print("crashed")
        return 0 

        
"""Watched this YouTube video to train and recognize faces
   https://www.youtube.com/watch?v=4W5M-YaJtIA&t=57s"""
        
def datasetGenerator(id):
        
    #Names files with users inputted name
    name = input("Enter name:")
    sampleNum = 0
    maxImages = 20
    
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            sampleNum += 1
            # Saves the captured images in the dataset folder using users id
            cv2.imwrite("trainer/User" + "." + str(name) + "." + str(id) + "." + str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
            # W
            cv2.waitKey(100)
        cv2.waitKey(1)
        # Takes twenty smaple pics of each user
        if sampleNum >= maxImages:
            return name
                
def getImagesAndLabels(path):
    # Get the path of each file in the folder
    imagePaths = [os.path.join(path,file) for file in os.listdir(path)]
    
    faceSamples, ids = [], []
    
    for path in imagePaths:
        # Loads the image and converts it to grayscale
        pilImage = Image.open(path).convert("L")
        # Converts PIL image into a numpy array
        array = np.array(pilImage, "uint8")
        # Gets the the user's name from the image
        id = int(os.path.split(path)[-1].split(".")[2])
        faceSamples.append(array)
        ids.append(id)
        # Extracts a face from the image samples 
        faces = faceCascade.detectMultiScale(array)
    return (faceSamples, ids)

faces, ids = getImagesAndLabels("trainer")
recognizer.train(faces, np.array(ids))
recognizer.save("recognizer/trainingData.yml")
            
# Takes in a dictionary of ids to users and matches them
def recognizeFace(users):
    
    while True:
        name = ""
        # Reads image
        ret, frame = cap.read()
        # Converts image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detects face in the captured frame
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        # If any faces detected, returns True
        for (x, y, w, h) in faces:
            # Uses the recognizer to predict user
            id, conf = recognizer.predict(gray[y:y+h,x:x+w])
            # If id found should be in dict but checks to avoid errors
            if str(id) in users:
                name = users[str(id)]
            # If id not detected uses "User" as the generic name
            else:
                name = "User"
        return name
    
