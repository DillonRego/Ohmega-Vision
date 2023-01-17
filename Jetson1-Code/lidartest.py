import lidar

lidar.start_vision_pipe(640,480,640,480)
i = 10
while(i != 0):
    lidar.object_detection()
    i = i - 1
lidar.end_vision_pipe()
