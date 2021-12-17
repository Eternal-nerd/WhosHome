import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import face_recognition
import boto3
import io
import os
import time
import shutil
from datetime import datetime
from bs4 import BeautifulSoup


IMAGE_COUNT = 0
mylesList = []
joeList = []
bucket_name = 'webserver-whoshome'
aws_access='AKIAYBUUGXQQ7JC2Y3UV'
aws_secret='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'
s3 = boto3.resource('s3', aws_access_key_id=aws_access, aws_secret_access_key=aws_secret)
bucket = s3.Bucket(bucket_name)
time_last_mod = None

def bucket_isempty():
    if len(list(bucket.objects.all())) == 0:
        return(True)
    else:
        return(False)
    
def check_s3_updates():
    if bucket_isempty():
        return(None)
        
    objects = list(bucket.objects.all())
    return(max(obj.last_modified for obj in objects))
    
#used for download_all
def get_recent_folder():
    if (bucket_isempty()):
        return(None)
    latest = []
    objects = list(bucket.objects.all())
    for obj in objects:
        if (len(latest) == 0):
            latest.append(obj)
        else:
            if obj.last_modified > latest[0].last_modified:
                latest[0] = obj
    return(obj.key.split("/")[2])
    
def update_site():
    shutil.copy("/home/ubuntu/index.html", "/var/www/html/index.html")
    
def get_encoded_lists():
    for filename in os.listdir('myles2'):
        tempImg = face_recognition.load_image_file(f"myles2/{filename}")
        tempImg = cv2.cvtColor(tempImg, cv2.COLOR_BGR2RGB)
        #tempImg = cv2.resize(tempImg, dsize=(730, 547), interpolation=cv2.INTER_CUBIC)
        #tempImg = cv2.rotate(tempImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
        if len(face_recognition.face_encodings(tempImg)) != 0:
            mylesList.append(face_recognition.face_encodings(tempImg)[0])
            
    for filename in os.listdir('joe2'):
        tempImg = face_recognition.load_image_file(f"joe2/{filename}")
        tempImg = cv2.cvtColor(tempImg, cv2.COLOR_BGR2RGB)
        #tempImg = cv2.resize(tempImg, dsize=(730, 547), interpolation=cv2.INTER_CUBIC)
        #tempImg = cv2.rotate(tempImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
        if len(face_recognition.face_encodings(tempImg)) != 0:
            joeList.append(face_recognition.face_encodings(tempImg)[0])
            

def download_all_objects_in_imagefolder(foldername):
        objects = bucket.objects.filter(Prefix=f'resources/imagefolders/{foldername}/') #FIXME 
        for obj in objects:
            path, filename = os.path.split(obj.key)
            bucket.download_file(obj.key, filename)
            
            
#MUST GET MYLES LIST FIRST
def compare_myles(encoded):
    tempList = face_recognition.face_distance(mylesList, encoded)
    avg = 0 
    for i in tempList:
        avg+=i
    avg = avg/len(tempList)
        
    if (avg < 0.55):
        return(True)
    else:
        return(False)
    
#MUST GET JOE LIST FIRST
def compare_joe(encoded):
    tempList = face_recognition.face_distance(joeList, encoded)
    avg = 0 
    for i in tempList:
        avg+=i
    avg = avg/len(tempList)
        
    if (avg < 0.55):
        return(True)
    else:
        return(False)

def check_faces():
    needImg = True
    count = 0
    countJoe = 0
    countMyles = 0
    #currentTime = time.strftime("%H:%M:%S_%d-%m-%Y", time.localtime())
    global IMAGE_COUNT
    
    
    for i in range(5):
        filename = f"image{i}.jpg"
        tempImg = face_recognition.load_image_file(filename)
        tempImg = cv2.cvtColor(tempImg, cv2.COLOR_BGR2RGB)
        
        if (len(face_recognition.face_encodings(tempImg)) != 0):
            encodeTest = face_recognition.face_encodings(tempImg)[0]
            #print(f'FACE FOUND IN {filename}')
            
            if (compare_joe(encodeTest)):
                countJoe+=1
                #print('we found a joe')
            if (compare_myles(encodeTest)):
                #print("we found a myles")
                countMyles+=1
                
            if (needImg):
                shutil.move(filename, f"images/image{IMAGE_COUNT}.jpg")
                needImg = False
            else:
                os.remove(filename)
            
                
        else:
            if count == 4:
                shutil.move(filename, f"images/image{IMAGE_COUNT}.jpg")
                count+=1
            else:
                os.remove(filename)
                count+=1
            
    if (count == 5):
        return("Unknown")

            
    if (countMyles + countJoe == 0):
        return("Unknown Person")
        
    if ((countMyles + countJoe != 0) and (countMyles==countJoe)):
        return("Unknown Person")
        
    if (countJoe>countMyles):
        return("Joe")
        
    if (countJoe<countMyles):
        return("Myles")
    
    
def check_five():
    for i in range(5):
        if (not os.path.isfile(f"image{i}.jpg")):
            return(False)
    return(True)


# STUFF IN THE WHILE LOOP


#check_faces()
#update_site()
#quit()

get_encoded_lists()
#check_faces()

#quit()
while True:
    if check_s3_updates() == time_last_mod:
        time.sleep(5)
        print("i sleep")
        
    else:
        print("Update detected")
        time_last_mod = check_s3_updates()
        
        #get latest image folder name
        temp_folder_name = get_recent_folder()
        print(f"folder name: {temp_folder_name}")
        
        if (temp_folder_name!=None):
            
            #download all images from it
            download_all_objects_in_imagefolder(temp_folder_name)
            
            while not check_five():
                time.sleep(5)
                download_all_objects_in_imagefolder(temp_folder_name)
            
            result = check_faces()
            
            imDir = f"images/image{IMAGE_COUNT}.jpg"
            
            currentTime = time.strftime("%H:%M:%S on %m-%d-%Y", time.localtime())
            
            if (result == "Unknown"):
                tmpImg = face_recognition.load_image_file(imDir)
                tmpImg = cv2.cvtColor(tmpImg, cv2.COLOR_RGB2BGR)
                cv2.putText(tmpImg, f'{result}', (0, 440), cv2.FONT_HERSHEY_PLAIN, 6, (0, 0, 255), 10)
                cv2.putText(tmpImg, f'Time of departure: {currentTime}', (0, 475), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                cv2.imwrite(imDir, tmpImg)
            else:
                tmpImg = face_recognition.load_image_file(imDir)
                faceLoc = face_recognition.face_locations(tmpImg)[0]
                tmpImg = cv2.cvtColor(tmpImg, cv2.COLOR_RGB2BGR)
                cv2.rectangle(tmpImg, (faceLoc[3], faceLoc[0]), (faceLoc[1], faceLoc[2]), (0, 0, 255), 2)
                cv2.putText(tmpImg, f'{result}', (0, 440), cv2.FONT_HERSHEY_PLAIN, 8, (0, 0, 255), 10)
                cv2.putText(tmpImg, f'Time of arrival: {currentTime}', (0, 475), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)
                cv2.imwrite(imDir, tmpImg)
            
            print(result)
        
            shutil.copy(imDir, f'/var/www/html/images/image{IMAGE_COUNT}.jpg')
            
            with open('index.html') as inf:
                txt = inf.read()
                soup = BeautifulSoup(txt ,features="html.parser")
            
                
                new_tag = soup.new_tag("img", src=f"/images/image{IMAGE_COUNT}.jpg")
                soup.body.append(new_tag)
                
                
                
            with open("index.html", "w") as outf:
                outf.write(str(soup))
                
            update_site()
            print("site updated.")
            

            time_last_mod = check_s3_updates()
            IMAGE_COUNT += 1
            time.sleep(15)
            
        
