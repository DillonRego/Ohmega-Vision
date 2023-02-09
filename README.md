# Jetson Code Repository

## Current Usable Files
- `main.cpp` and `run.sh`. These files run the cpp code developed last year. This code works but is not very powerful or efficient. 
- `lidar.py` rudimentary python LiDAR controller


## Python Instructions 
- librealsense2 library is required via instructions here https://github.com/IntelRealSense/librealsense/issues/6964 and https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python#installation
- Note: path exports are required (these have been done on the jetson)
- Python3.8 and python3.8-dev were used in development


## Putty install: 
- https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html, 
- First link: https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.77-installer.msi
- Unbuntu version 18.04.06

## Jetson nano1 (insert model number)
- Python 3.8.0
- Pytorch 1.12.1
- pyrealsense2 2.51.1
- cv2 4.6.0
- Intel Realsense d405

## How to connect to the Jetson Nano:
- Open putty, open device manager find the port under ports com and lpt
- Set the connection type to `serial`, and change the serial line to whatever you found in device manager and change speed to `11520`
- Then login: `herbie (username)`, `mars2021 (password)`

## ssh into Jetson Nano
- Jetson nano must have internet access
- If passing internet connection throught PC onto nano using an Ethernet cable
- Go to Network Connectons -> under wifi click properties -> sharing -> check Allow internet connection settings
- Jetson Nano 1
- `~$ ssh herbie@192.168.137.76`
- `~$ ssh herbie@192.168.137.224`
- Jetson Nano 2
- `~$ ssh herbie@192.168.137.239`
- `~$ ssh herbie@192.168.137.51`

## Transfering files with github
- `git status` to check files that need to be added
- `git add <files>` to add files
- `git commit -m 'message'` to commit all files that have been added
- `git push` to push files to the repo

## Transfer files from Jetson Nano to local PC
- `~$ scp herbie@192.168.137.76:/targetfile /destination`

## Transfer files from local PC to Jetson Nano
- `~$ scp /targetfile herbie@192.168.137.76:~/destination`

## Access RealSense viewer
- `~$ realsense-viewer`

## Discrete Fourier Transform example using open cv
- https://docs.opencv.org/3.4/d2/de8/group__core__array.html#gadd6cf9baf2b8b704a11b5f04aaf4f39d

## Deep learning canny edge detection in open cv
- $ https://cv-tricks.com/opencv-dnn/edge-detection-hed/
- https://samuelabiodun.medium.com/edge-detection-techniques-image-processing-with-opencv-450e3ff8c601

## Training YOLOv5
Generic:
-https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-yolov5-object-detection-on-custom-data.ipynb
Specific:
-https://colab.research.google.com/drive/1RsylzAtXrJbDWdYRYt_aUFyMfdyvIyKN#scrollTo=1NcFxRcFdJ_O

## CUDA
- https://learnopencv.com/getting-started-opencv-cuda-module/

## DATASET
- https://universe.roboflow.com/tup/pvc-with-coupling

## Yolov5 link
- https://github.com/ultralytics/yolov5
## Jetson GPIO
-https://github.com/NVIDIA/jetson-gpio
-https://github.com/sparkfun/Qwiic_Py

## I2C Pins
-as of right now we are using I2C 1 on the Jetson (pins 27,28 and gnd)
-pins 3,5, 6 on the Raspberry pi

Look into this https://github.com/amaork/libi2c/blob/master/src/pyi2c.c

https://docs.nvidia.com/jetson/archives/r34.1/DeveloperGuide/index.html#page/Tegra%2520Linux%2520Driver%2520Package%2520Development%2520Guide%2Fkernel_custom.html%23


