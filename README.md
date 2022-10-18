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
- first link: https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.77-installer.msi
- Unbuntu version 18.04.06

## Jetson nano (insert model number)
- intel realsense d405

## how to connect to the jetson nano:
- open putty, open device manager find the port under ports com and lpt
- set the connection type to serial, and change the serial line to whatever you found in device manager and change speed to 11520
- then login: "herbie" (username), "mars2021" (password) for the loose nano.

## ssh into Jetson nano
-Jetson nano must have internet access
-If passing internet connection throught PC onto nano using an Ethernet cable
-go to Network Connectons -> under wifi click properties -> sharing -> check Allow internet connection settings
-~$ ssh herbie@192.168.137.76

## Transfer files from Jetson Nano to PC
-~$ scp herbie@192.168.137.76 /targetfile /destination

## Access RealSense viewer
-~$ realsense-viewer
