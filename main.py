import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-recognition-system.firebaseio.com/",
    'storageBucket':"face-recognition-system.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load the background image
background_image_path = "Resources/background.png"
imgBackground = cv2.imread(background_image_path)

# Resize the background image to your desired width and height
desired_width = 1280
desired_height = 720
imgBackground = cv2.resize(imgBackground, (desired_width, desired_height))

# Import mode images
folderModePath = "Resources/Modes"
modePathList = os.listdir(folderModePath)

imgModeList = []
for path in modePathList:
    img = cv2.imread(os.path.join(folderModePath, path))

    # Resize the mode image to fit the target region
    img = cv2.resize(img, (300, 433))  # Adjust dimensions as needed
    imgModeList.append(img)

# Load the encoding file
print("Loading the encoding file")
file = open("EncodeFile.p", "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
print("Loading complete")

encodeListKnown, idUserList = encodeListKnownWithIds

modeType = 0
count = 0
id = -1
imgUser = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

    imgBackground[168:168+480, 76:76+640] = img
    
    i1 = cv2.resize(imgModeList[modeType], (300, 433))
    imgBackground[188:188+433, 855:855+300] = i1

    for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

        # Draw a rectangle around the detected face
        bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
        cvzone.cornerRect(imgBackground, bbox, rt=0)
        # cv2.rectangle(imgBackground, (x1 + 76, y1 + 168), (x2 + 76, y2 + 168), (0, 255, 0), 2)

        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex] == True:
            id = idUserList[matchIndex]
            if count == 0:
                cvzone.putTextRect(imgBackground,"Loading",(275,400))
                cv2.imshow("Face Attendance", imgBackground)
                cv2.waitKey(1)
                count = 1
                modeType = 1
                
    if count != 0:
        if count == 1:
            # downloading data form firebase
            userInfo = db.reference(f'Users/{id}').get()
            # print(userInfo)
            blob = bucket.get_blob(f'Resources/Images/{id}.png')
            if blob is not None:
                blob_string = blob.download_as_string()
                array = np.frombuffer(blob_string, np.uint8)
                imgUser = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)      
            else:
                print(f"Blob 'Images/{id}.png' does not exist in the bucket.")
        
        if 15<count<30:
            modeType = 2
            i1 = cv2.resize(imgModeList[modeType], (300, 433))
            imgBackground[188:188+433, 855:855+300] = i1
        
        if count<=15:
            cv2.putText(imgBackground,str(userInfo['Name']), (1000,528), cv2.FONT_HERSHEY_COMPLEX, 0.6,1)
            cv2.putText(imgBackground,str(userInfo['Age']), (1000,563), cv2.FONT_HERSHEY_COMPLEX, 0.6,1)
            cv2.putText(imgBackground,str(userInfo['Gender']), (1000,595), cv2.FONT_HERSHEY_COMPLEX, 0.6,1)
            imgBackground[250:250+216,900:900+216] = imgUser
            
        count += 1  
        
        if count>=30:
            count = 0
            modeType = 0
            userInfo = []
            imgUser = []
            i1 = cv2.resize(imgModeList[modeType], (300, 433))
            imgBackground[188:188+433, 855:855+300] = i1
            
              
            
    # Display the resulting image
    cv2.imshow("Face Attendance", imgBackground)
    # cv2.waitKey(1)
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:  # 'q' key or ESC key
        break
    
    # Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
