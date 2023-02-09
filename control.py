import pyrealsense2 as rs
import numpy as np
import cv2
import time
import torch
import math
import edge

def collectTubeLocation(vis):
    consecutiveBad = 0
    consecutiveNone = 0
    good = 0
    cameraCords = 0
    realWorldCords = (0, 0, 0, 0)
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
            realWorldCords = tuple(sum(x) for x in zip(realWorldCords, data))
    if(consecutiveNone >= 10):
        return -1
    elif(consecutiveBad >= 10):
        return cameraCords
    else:
        return tuple(x/5 for x in realWorldCords)

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
                if unpacked[0].decode == "take_picture":
                    result = collectTubeLocation(vis)
                    if (result == -1):
                        I2C_write_packet("failure")
                    elif not isinstance(result, tuple):
                        I2C_write_packet(f'turn: {"left" if result < 0 else "right"}')
                    else:
                        I2C_write_packlet("loc: FIX THIS")
                
        time.sleep(i2c.timewait)

    return

if __name__ == '__main__':
    main()