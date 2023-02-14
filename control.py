import math
from Nano_I2C import *
from visionSystem import VisionSystem

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
    # Initialize the I2C bus
    i2c = Nano_I2CBus()
    # Initialize the Vision System
    vis = VisionSystem()

    while True:
        pkt = i2c.wait_response()

        if not pkt:
            return

        # If the packet isn't the target ID (pi) and it isn't a command
        if (pkt[I2CPacket.id_index].decode() != i2c.pkt_targ_id) or (pkt[I2CPacket.stat_index] != b'c'):
            return

        print('Command received:')

        data = pkt[I2CPacket.data_index].decode().strip('\0')

        print(data)

        # To Do: fix system commands and
        # Respond back to Jetson
        
        if data == 'get_tube':
            result = collectTubeLocation(vis)
            if result == -2:
                response = 'tube error'.encode()
            if result == -1:
                response = 'no tube'.encode()
            elif not isinstance(result, tuple):
                response = (f'turn: {"left" if result < 0 else "right"}').encode()
            else:
                response = 'XYZ'.encode() #To Do: fix return location cordinates
            i2c.write_pkt(response, 'd')
                
        elif data ==  'take_picture':
            result = vis.captureImage()
            
            response = 'Start'.encode()
            i2c.write_pkt(response, 'd')
            
            # I2C_save_image(result[0]) ADD THIS TO I2C
            response = 'Stop'.encode()
            i2c.write_pkt(response, 'd')
            
            
            response = 'Picture'.encode()
            i2c.write_pkt(response, 'd')
                
        else:
            response = 'Command not recognized'.encode()
            i2c.write_pkt(response, 'd')

if __name__ == '__main__':
    main()
