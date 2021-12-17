from gpiozero import MotionSensor, RGBLED
from picamera import PiCamera
from PIL import Image
import time
import os
import shutil
import boto3
import requests
from boto3.s3.transfer import TransferConfig

#multipart threshold val
GB = 1024 ** 3
config = TransferConfig(multipart_threshold=5*GB)

bucket_name = 'webserver-whoshome'

pir = MotionSensor(24)
led = RGBLED(red=9, green=10 , blue=11)
camera = PiCamera()
index = 1

#make sure internet connection is present
led.red = 0.1
while True:
    try:
        requests.get('https://www.google.com/').status_code
        break
    
    except:
        led.red = 0
        time.sleep(1)
        led.red = 0.1
        time.sleep(1)
        pass

led.red = 0
    

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_name)
    
    s3 = boto3.client('s3', aws_access_key_id='AKIAYBUUGXQQ7IHZUIFR', aws_secret_access_key='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')
    
    s3.upload_file(file_name, bucket, object_name)
        
#empty bucket before starting
s3 = boto3.resource('s3', aws_access_key_id='AKIAYBUUGXQQ7IHZUIFR', aws_secret_access_key='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')
bucket = s3.Bucket(bucket_name)
bucket.objects.all().delete()

#main program
while(True):
    
    led.blue = 0.1
    
    pir.wait_for_motion() #detects motion
    
    led.blue = 0
    led.green = 0.1
    
    filenames = []
    
    currentTime = time.strftime("%H:%M:%S %d-%m-%Y", time.localtime())
    print(f"\nMotion Detected, {index} occurances (time: {currentTime}).")
    
    #make a log file
    logfile = f"log{index}.txt"
    f = open(logfile,"w+")
    f.write(f"Motion detected at {currentTime}.")
    f.close()
    
    #capture images
    imgFolder = f"imagefolder{index}"
    
    if os.path.exists(imgFolder):
        shutil.rmtree(imgFolder)
    
    os.mkdir(imgFolder)
    
    #burst of images
    for i in range(5):
        led.green = 0
        
        imagefile = f"image{i}.jpg"
        camera.capture(imagefile)
        
        led.green = 0.1
        
        #rotate it cause im dumb
        img = Image.open(imagefile)
        out = img.rotate(180)
        out.save(imagefile)
        
        os.replace(imagefile, imgFolder + "/" + imagefile)
        
        print(f"Image {i} captured. ") 
    
    pir.wait_for_no_motion() #Not detecting motion anymore
    
    #send the files
    #upload_file(file_name=logfile, bucket=bucket_name, object_name='resources/logs/{}'.format(logfile))
    #print(f"Log file {index} sent succesfully.  ")
    
    for root, dirs, files in os.walk(imgFolder):
        for file in files:
            upload_file(file_name=os.path.join(root, file), bucket=bucket_name, object_name=f'resources/imagefolders/{imgFolder}/{file}')
        
    print(f"Image folder {index} sent succesfully.  ") 
    

    #delete files after
    os.remove(logfile)
    shutil.rmtree(imgFolder)
        
    #give time to reset everything serverside
    time.sleep(25)
    
    led.green = 0
    led.blue = 0.1
    index += 1


