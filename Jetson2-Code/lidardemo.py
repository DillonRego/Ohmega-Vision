import pyrealsense2 as rs
import numpy as np
import cv2

LOOP = True

# CONSTANTS 
WARMUP_FRAMES = 10
# These values are limited rn by USB 2 connection 
STREAM_WIDTH = 320
STREAM_DEPTH = 240
STREAM_FPS = 30

# This changes the min distance that is colorized on the depth-frame
VIZ_MIN = 45

# We want to remove the background reading of objects more than MAX_RANGE_METERS away 
# this is recalculated to MAX_RANGE in depth_units
MAX_RANGE_METERS = 2

# Create and configure Pipeline
pipe = rs.pipeline()
config = rs.config() # TO-DO look into configuration options here

# Stream enabling and resolution setting
# https://intelrealsense.github.io/librealsense/doxygen/classrs2_1_1config.html
config.enable_stream(rs.stream.depth, 0, 0, rs.format.z16, STREAM_FPS)
config.enable_stream(rs.stream.color, 0, 0, rs.format.bgr8, STREAM_FPS)

# Start Pipeline
profile = pipe.start(config)

# Used to configure depth sensor 
depth_sensor = profile.get_device().first_depth_sensor()

depth_scale = depth_sensor.get_depth_scale()

MAX_RANGE = MAX_RANGE_METERS / depth_scale

# Min Distance Test
if depth_sensor.supports(rs.option.min_distance):
    min_dist = depth_sensor.get_option(rs.option.min_distance)
    print("min_distance = %d" % min_dist)
    min_dist = depth_sensor.set_option(rs.option.min_distance, VIZ_MIN)
    min_dist = depth_sensor.get_option(rs.option.min_distance)
    print("New min_distance = %d" % min_dist)

# Warmup 
for x in range(WARMUP_FRAMES):  
    pipe.wait_for_frames()

try:
    while True:
        frameset = pipe.wait_for_frames()

        # Alignment test - Aligning to color stream
        align = rs.align(rs.stream.color)

        aligned_frames = align.process(frameset)
        color_frame = aligned_frames.get_color_frame() 
        aligned_depth_frame = aligned_frames.get_depth_frame()

        # print("Color Width " + str(color_frame.get_width()))
        # print("Color Height " + str(color_frame.get_height()))
        # print("Depth Width " + str(depth_frame.get_width()))
        # print("Depth Height " + str(depth_frame.get_height()))

        # # RealSense Colorizer Test
        # colorizer = rs.colorizer()
        # colorizer.set_option(rs.option.visual_preset, 1)
        # colorizer.set_option(rs.option.min_distance, VIZ_MIN)

        #convert frams to numpy-arrays
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Remove Depth Background 
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image)) # convert 1-channel depth map to 3channel
        bg_removed = np.where((depth_image_3d > MAX_RANGE) | (depth_image_3d <= 0), grey_color, color_image)

        #colorize depth map https://learnopencv.com/applycolormap-for-pseudocoloring-in-opencv-c-python/
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)


        # B&W CONTOUR TESTS

        depth_graymaprgb = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_BONE)
        depth_graymap = cv2.cvtColor(depth_graymaprgb, cv2.COLOR_BGR2GRAY)


        # Temporary downscaling of color frame to match with depth-frame

        # depth_colormap_dim = depth_colormap.shape
        # color_colormap_dim = color_image.shape
        # resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)

        images = np.hstack((bg_removed, depth_colormap))

        # Don't Remember what this is for

        # sourceFile = open('test.txt', 'w')
        # np.set_printoptions(threshold=np.inf)
        # print(depth_graymap, file = sourceFile)
        # sourceFile.close()


        # Filters on depth-map 

        res1 = cv2.inRange(depth_graymap, 1, 150) # blacks out everything out of range, makes white everything IN RANGE
        contours,hierarchy = cv2.findContours(res1,2,1)
        cv2.drawContours(depth_graymaprgb, contours, -1, (0,255,0), 3)

        cv2.namedWindow('Color', cv2.WINDOW_NORMAL)
        cv2.namedWindow('Depth', cv2.WINDOW_NORMAL)
        #Display Depth and Color Map
        cv2.imshow('Color', color_image)
        cv2.imshow('Depth', depth_image)

        cv2.namedWindow('Align Test', cv2.WINDOW_NORMAL)
        #Display Depth Filtering Stuff
        cv2.imshow('Align Test', images)

        cv2.namedWindow('Bordering', cv2.WINDOW_NORMAL)
        cv2.imshow('Bordering', depth_graymaprgb)

        cv2.waitKey(int(LOOP))

finally:
    pipe.stop()

