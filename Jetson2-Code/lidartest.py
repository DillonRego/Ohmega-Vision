import lidar

# using worse lidar so default these values to 0
lidar.start_vision_pipe()
while(True):
    lidar.object_detection()
lidar.end_vision_pipe()
