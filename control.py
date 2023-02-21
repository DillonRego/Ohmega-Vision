import math
import cv2
from Nano_I2C import *
from visionSystem import VisionSystem

#Offset in centimeters
offset_x = 2.9
offset_y = 4.9
offset_z = 23.544
camera_angle = math.radians(65)

def get3Dlocation(realWorldCords):
    return (realWorldCords[0] ** 2 + realWorldCords[1] ** 2 + realWorldCords[2] ** 2) ** 0.5

def translateCoordinates(x, y, depth):
        camera_hyp = (x ** 2 + y ** 2) ** 0.5
        center_depth = (depth ** 2 - camera_hyp ** 2) ** 0.5
        real_z = center_depth * math.cos(camera_angle + math.atan(y/center_depth))
        groundhyp = depth * math.sin(camera_angle + math.atan(y/center_depth))
        real_y = (groundhyp ** 2 - x ** 2) ** .5
        return x + offset_x, real_y + offset_y, -real_z + offset_z

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
            realWorldCords[good] = translateCoordinates(data[0], data[1], data[2]) + (data[3])#tuple(sum(x) for x in zip(realWorldCords, data))
            good+=1
            consecutiveBad = 0
            consecutiveNone = 0
    if(consecutiveNone >= 10):
        return -1
    elif(consecutiveBad >= 10):
        return cameraCords
    else:
        return checkTubeLocationValidity(realWorldCords)#tuple(x/5 for x in realWorldCords)

def main():
    # Initialize the I2C bus
    i2c = Nano_I2CBus()
    # Initialize the Vision System
    vis = VisionSystem()

    while True:
        pkt = i2c.wait_response()

        if not pkt:
            continue

        # If the packet isn't the target ID (pi) and it isn't a command
        if (pkt[I2CPacket.id_index].decode() != i2c.pkt_targ_id) or (pkt[I2CPacket.stat_index] != b'c'):
            continue

        print('Command received:')

        data = pkt[I2CPacket.data_index].decode().strip('\0')

        print(data)
        
        # Read command and respond back to Pi
        if data == 'cord':
            result = collectTubeLocation(vis)
            #result = 0
            if result == -2:
                response = 'error'.encode()
            if result == -1:
                response = 'none'.encode()
            elif not isinstance(result, tuple):
                response = (f'turn: {"left" if result < 0 else "right"}').encode()
            else:
                response = 'xyz'.encode() #To Do: fix return location cordinates
            i2c.write_pkt(response, 'd', 0)
                
        elif data ==  'img':
            result = vis.captureImage()
            filename = time.strftime("%Y%m%d-%H%M%S") + '.JPG'
            cv2.imwrite(filename, result[0])
            i2c.file_send(filename)
                
        else:
            response = 'Command not recognized'.encode()
            i2c.write_pkt(response, 'd', 0)

if __name__ == '__main__':
    main()
