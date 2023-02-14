import pyrealsense2 as rs
import numpy as np
import cv2
import time
import torch
import math
import edge

def get3Dlocation(realWorldCords):
    return (realWorldCords[0] ** 2 + realWorldCords[1] ** 2 + realWorldCords[2] ** 2) ** 0.5

def translateCoordinates(x, y, depth):
        real_z = depth * math.sin(camera_angle)
        groundhyp = depth * math.cos(camera_angle)
        real_y = (groundhyp ** 2 - real_x ** 2) ** .5
        return x, real_y, real_z

def checkTubeLocationValidity(realWorldCords):
    match = [0] * 5
    threshold = 10
    matchAmount = 0
    result = (0, 0, 0)
    for i in range(5):
        for j in range(5):
            if j != i :
                if abs(get3Dlocation(realWorldCords[i]) - get3Dlocation(realWorldCords[j])) < threshold:
                    match[i] = 1
        for k in range(5):
            if match[k] == 1:
                tuple(sum(x) for x in zip(realWorldCords[k], result))
                matchAmount+=1
                match[k] = 0
        if matchAmount >= 3:
            return result
        else:
            matchAmount = 0
            result = (0, 0, 0)
    return -2

def collectTubeLocation(vis):
    consecutiveBad = 0
    consecutiveNone = 0
    good = 0
    cameraCords = 0
    realWorldCords = [(0, 0, 0, 0)] * 5
    while(good < 5 and consecutiveBad < 10 and consecutiveNone < 10):
        data = vis.processOneFrame()
        if(data[2] == - 1):
            consecutiveNone+=1
        elif(data[2] == 0):
            consecutiveBad+=1
            cameraCords+=data[0]/10
        else:
            good+=1
            consecutiveBad = 0
            consecutiveNone = 0
            realWorldCords[i] = translateCoordinates(data[0], data[1], data[2])#tuple(sum(x) for x in zip(realWorldCords, data))
    if(consecutiveNone >= 10):
        return -1
    elif(consecutiveBad >= 10):
        return cameraCords
    else:
        return checkTubeLocationValidity(realWorldCords)#tuple(x/5 for x in realWorldCords)

def main():
    vis = VisionSystem()
    while True:
        data_received = i2c.read_pkt()
        
        if len(data_received) == 0:
            print('No data received!')
        else:
            # Verify the received packet
            if I2CPacket.verify_pkt(data_received) == False:
                print('Packet corrupted!')
            else:
                # Unpack the received packet
                unpacked = I2CPacket.parse_pkt(data_received)
                print(f'Data received: {unpacked[0].decode()}')
                if unpacked[0].decode == "get_tube":
                    result = collectTubeLocation(vis)
                    if result == -2:
                        I2C_write_packet("error")
                    if result == -1:
                        I2C_write_packet("failure")
                    elif not isinstance(result, tuple):
                        I2C_write_packet(f'turn: {"left" if result < 0 else "right"}')
                    else:
                        I2C_write_packlet("loc: FIX THIS")
                elif unpacked[0].decode == "take_picture":
                    result = vis.captureImage()
                    I2C_write_packet("start")
                    I2C_save_image(result[0])
                    I2C_write_packet("stop")
                
        time.sleep(i2c.timewait)

    return

if __name__ == '__main__':
    main()
