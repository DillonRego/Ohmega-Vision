# Jetson Code Repository

## Current Usable Files
- `boot.sh`,`control.py`, and `Nano_I2C.py`. 
- `visionSystem.py` rudimentary python Vision System controller

## Python Instructions 
- Note: path exports are required (these have been done on the jetson)
- librealsense2 library is required via instructions here https://github.com/IntelRealSense/librealsense/issues/6964 and https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python#installation
- Python3.8 and python3.8-dev were used in development

## Jetson Nano System Requuirements
- Python 3.8.0
- Pytorch 1.12.1
- pyrealsense2 2.51.1
- cv2 4.6.0
- Intel Realsense d405

## I2C Pins
- As of right now we are using I2C 1 on the Jetson (pins 27,28 and gnd)
- Pins 3,5, 6 on the Raspberry pi

## How to connect to the Jetson Nano via ssh:
- Jetson nano must have internet access
- If passing internet connection throught PC onto nano using an Ethernet cable
- Go to Network Connectons -> under wifi click properties -> sharing -> check Allow internet connection settings
- Jetson Nano 1
- `~$ ssh herbie@192.168.137.76`
- `~$ ssh herbie@192.168.137.224`
- Jetson Nano 2
- `~$ ssh herbie@192.168.137.239`
- `~$ ssh herbie@192.168.137.51`
- Then login: `herbie (username)`, `mars2021 (password)` or `mars2022 (password)`

## Transfering files with github
- `git status` to check files that need to be added
- `git add <files>` to add files
- `git commit -m 'message'` to commit all files that have been added
- `git push` to push files to the repo

## Transfer files from Jetson Nano to local PC via scp
- `~$ scp herbie@192.168.137.76:/targetfile /destination`

## Transfer files from local PC to Jetson Nano via scp
- `~$ scp /targetfile herbie@192.168.137.76:~/destination`

## Access RealSense viewer
- `~$ realsense-viewer`

## Training YOLOv5
Generic:
-https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-yolov5-object-detection-on-custom-data.ipynb
Specific:
-https://colab.research.google.com/drive/1RsylzAtXrJbDWdYRYt_aUFyMfdyvIyKN#scrollTo=1NcFxRcFdJ_O

## DATASET
- https://universe.roboflow.com/tup/pvc-with-coupling

## Yolov5 link
- https://github.com/ultralytics/yolov5
## Jetson GPIO
-https://github.com/NVIDIA/jetson-gpio
-https://github.com/sparkfun/Qwiic_Py

Look into this https://github.com/amaork/libi2c/blob/master/src/pyi2c.c

https://docs.nvidia.com/jetson/archives/r34.1/DeveloperGuide/index.html#page/Tegra%2520Linux%2520Driver%2520Package%2520Development%2520Guide%2Fkernel_custom.html%23


