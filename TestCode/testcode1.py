import cv2
import pyrealsense2 as rs
#from realsense_depth import *

# initialize intel real sense camera
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))
print(device_product_line)

ret, depth, frame, color_frame = device.get_frame()

cv2.imshow("Color frame", color_frame)
cv2.waitkey(0)
