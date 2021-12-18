# Who's Home

Who's Home is a roommate tracking app with the goal of enabling an individual to see who is home and who is not.  

## Installation

___NOTE: This project is highly personalized to our specific use, and will require a fair amount of work to be used in a different environment.___

__Install necessary libraries to your Ubuntu EC2 instance:__

  - opencv-python
  - face_recognition
  - boto3
  - beautifulsoup4
  - awscli
  - cmake
  - dlib

_(all of these can be installed using pip installer ```sudo apt install python3-pip```)_

__Install Apache2:__

```bash
sudo apt-get update
sudo apt-get install apache2
```

Create a bucket using AWS S3 storage and modify _EC2 Python Script.py_ to use it.

Once the EC2 instance an, place _EC2 Python Script.py_ on the EC2 instance and _Raspi Python Script.py_ on the Raspberry Pi and run them (how the sensors are wired to the Raspberry Pi may require the code to be slightly modified).

_index.html_ will need to be placed in ```/var/www/html``` directory.

Custom datasets will need to be created for each person needing to be identified. 

_The code will need to be heavily modified to utilize these new datasets._

## Usage

Once the Python scripts are running on their respective machines, the system will run automatically.  Users may check the website hosted by their EC2 instance to see the last time the motion sensor was set off, the best image it took, and what the face-recognition found from identifying the image.  

__The four states we implemented are:__

* Joe 
* Myles
* Unknown person (face detected, but not close to any faces in dataset)
* Unknown (no face detected)

If a face is detected, it is assumed that someone has entered the apartment, so the website will display the time of arrival.  If no face is detected, it is assumed that it is a departure, and it is up to the user to determine who it is in the image leaving the apartment.  
