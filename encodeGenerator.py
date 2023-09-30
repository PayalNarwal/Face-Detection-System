import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://face-recognition-system.firebaseio.com/",
    'storageBucket':"face-recognition-system.appspot.com"
})

# Import users images
folderImagesPath = "Resources/Images"
userPathList = os.listdir(folderImagesPath)

imgUserList = []
idUserList = []
for path in userPathList:
    img = cv2.imread(os.path.join(folderImagesPath, path))
    # Resize the mode image to fit the target region
    img = cv2.resize(img, (410, 633))  # Adjust dimensions as needed
    imgUserList.append(img)
    
    # print(path)
    # print(os.path.splitext(path)[0])
    idUserList.append(os.path.splitext(path)[0])
    
    fileName = f'{folderImagesPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
    
# print(idUserList)
# print(len(imgUserList))  #->2

def findEncoding(imagesList):
    encodeList = []
    count = 0
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
            count +=1
            print(f"Face found in {count} - appending")
            
        except IndexError:
            count +=1
            print(f"No face found in {count} - skipping")
        # encode = face_recognition.face_encodings(img)[0]
        # encodeList.append(encode)
    return encodeList
        
print("Encoding started")
encodeListKnown = findEncoding(imgUserList)
encodeListKnownWithIds = [encodeListKnown , idUserList]
# print(encodeListKnown)
print("Encoding complete")

file = open("EncodeFile.p","wb")
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File saved")
