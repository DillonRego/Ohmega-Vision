# Jetson Code Repository

## Current Usable Files
- `boot.sh` runs `control.py` off boot.
- `control.py` uses `Nano_I2C.py`, `visionSystem.py` and `edge.py`. 
- `visionSystem.py` rudimentary python Vision System.
- `streamAndNetV5.py` used to vizualize the object Detection.
- `i2c_bus.py` used on a rasppberry pi to test our `Nano_I2C.py`.

## Jetson Nano System Requuirements
- Python 3.8.0
- Pytorch 1.12.1
- pyrealsense2 2.51.1
- cv2 4.6.0
- Intel Realsense d405

## Python Instructions 
- Note: path exports are required (these have been done on the jetson)
- librealsense2 library is required via instructions here https://github.com/IntelRealSense/librealsense/issues/6964 and https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python#installation
- Python3.8 and python3.8-dev were used in development

## I2C Pins
- As of right now we are using eeprom buffer on the Jetson for I2C (pins 27,28 and gnd).
- Pins 3, 5 and 6 on the Raspberry pi.

## How to connect to the Jetson Nano via ssh:
- Jetson nano must have internet access
- If passing internet connection throught PC onto nano using an Ethernet cable
- Go to Network Connectons -> under wifi click properties -> sharing -> check Allow internet connection settings
- `ifconfig` to get the ip of the jetson.
- `~$ ssh herbie@192.168.137.xxx`
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

## Yolov5 link
- https://github.com/ultralytics/yolov5

