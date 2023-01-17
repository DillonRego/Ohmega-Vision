import sys
sys.path.append('/usr/local/lib/python3.6/pyrealsense2')
import pyrealsense2 as rs
import numpy as np
import imageio
import cv2

WARMUP_FRAMES = 10
STREAM_FPS = 30
VIZ_MIN = 45

# Function to start the realsense pipeline
# Takes optional input paramaters of the desired stream resolutions
# Normally 1280, 720, 640, 480
def start_vision_pipe(c_width=0, c_height=0, d_width=0, d_height=0):
    global pipe 
    global depth_scale
    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, d_width, d_height, rs.format.z16, STREAM_FPS)
    config.enable_stream(rs.stream.color, c_width, c_height, rs.format.bgr8, STREAM_FPS)
    profile = pipe.start(config)
    depth_sensor = profile.get_device().first_depth_sensor()

    # Min Distance Test
    if depth_sensor.supports(rs.option.min_distance):
        min_dist = depth_sensor.get_option(rs.option.min_distance)
        print("min_distance = %d" % min_dist)
        min_dist = depth_sensor.set_option(rs.option.min_distance, VIZ_MIN)
        min_dist = depth_sensor.get_option(rs.option.min_distance)
        print("New min_distance = %d" % min_dist)

    depth_scale = depth_sensor.get_depth_scale()
    print(f"Depth Scale:{depth_scale}")

    #warmup
    for x in range(WARMUP_FRAMES):
        pipe.wait_for_frames()

def end_vision_pipe():
    if ('pipe' in globals()):
        pipe.stop()

def save_rgb_frame():
    if ('pipe' in globals()):
        frameset = pipe.wait_for_frames()
        color_frame = frameset.get_color_frame()
        color_image = np.asanyarray(color_frame.get_data())
        imageio.imwrite("rgb.jpeg", color_image)

def save_depth_frame():
    if ('pipe' in globals()):
        frameset = pipe.wait_for_frames()
        depth_frame = frameset.get_depth_frame()
        depth_data = np.asanyarray(depth_frame.get_data())
        depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_data, alpha=0.03), cv2.COLORMAP_JET)
        imageio.imwrite("depth.jpeg", depth_image)

def object_detection(demo=False):
    if ('pipe' in globals()):
        align = rs.align(rs.stream.color)
        frameset = pipe.wait_for_frames()
        frameset = align.process(frameset)
        depth_frame = frameset.get_depth_frame()
        depth_data = np.asanyarray(depth_frame.get_data())
        color_frame = frameset.get_color_frame()
        color_data = np.asanyarray(color_frame.get_data())

        # CV Setup 
        height, width = color_data.shape[:2]
        net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')
        inScaleFactor = 0.007843
        meanVal       = 127.53

        blob = cv2.dnn.blobFromImage(color_data, inScaleFactor, (300, 300), meanVal, False)
        net.setInput(blob, "data")
        detections = net.forward("detection_out")

        result = []

        for detection in detections[0,0]:
            confidence = float(detection[2])
            if confidence > 0.8:
                #print("object found")
                xmin  = abs(int(detection[3] * width))
                ymin  = abs(int(detection[4] * height))
                xmax  = abs(int(detection[5] * width))
                ymax  = abs(int(detection[6] * height))
                cv2.rectangle(color_data, (xmin, ymin), (xmax, ymax), (255, 255, 255), 2)
                # cv2.rectangle(depth_data, (xmin, ymin), (xmax, ymax), 10000, 2)
                # We just care about the depth now, not it's position so we can flatten and sourt this array
                object_depth = depth_data[ymin:ymax, xmin:xmax]
                object_depth = object_depth * depth_scale
                flat_depth = object_depth.flatten()

                # Zero Count 
                zero_count = len(flat_depth[flat_depth==0])
                if ((zero_count / len(flat_depth)) < 0.9):
                    dist = cv2.mean(flat_depth[flat_depth!=0])
                else:
                    dist = [0]


                middle = (xmax + xmin)/2
                if middle > (width/2):
                    direction = "right"
                else:
                    direction = "left"
                cv2.putText(color_data, f"Depth: {dist[0]:.3f} m Direction: " + direction, (int(xmin), int(ymin)-5), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255,255,255))
                # Return Type List [Float: Distance to Object, String: Object is left/right of center]
                # Only add if the distance is greater than 0 -> This is a result of detecting objects outside the LIDAR range
                if (dist[0] > 0):
                    result.append([dist[0], direction])

        # sort result list by distance
        result.sort()
        cv2.imshow('Output', color_data) 
        depth_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_data, alpha=0.03), cv2.COLORMAP_TWILIGHT_SHIFTED)
        cv2.imshow('Output2', depth_image)
        cv2.waitKey(1) # wait a set number of milliseconds to allow image to display
        #print(result)
        return result
