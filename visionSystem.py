import pyrealsense2 as rs
import numpy as np
import cv2
import time
import torch
import math
import edge

class VisionSystem:
    def __init__(self, directoryOfNNWeights= '/home/herbie/OVision2022/pyrealsense/librealsense-2.51.1/build/', nameOfWeights="best.pt"):
        self.model = torch.hub.load(directoryOfNNWeights, 'custom',
                               path=nameOfWeights,
                               source='local')
        self.pipeline = rs.pipeline()
        config = rs.config()

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    def processOneFrame(self):
        '''
        Processes a frame and returns the x, y, depth, orientation
        3 possible outputs
            int, int, int, int -> found a tube and all relevant info
            int, int, 0, int -> found a tube but couldnt get depth info
            -1, -1, -1, -1 -> no tube found
        '''
        color_frame, depth_frame = self.captureImage()
        results = self.checkForTube(color_frame)
        return self.getTubeData(color_frame, depth_frame, results)

    def captureImage(self):
        self.pipeline.start(config)
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        self.pipeline.stop()
        return color_frame, depth_frame

    def checkForTube(self, color_frame):
        color_image = np.asanyarray(color_frame.get_data())
        results = model(color_image)
        results.render()
        return results.xyxy

    def getTubeData(self, color_frame, depth_frame, tubeResults):
        if len(tubeResults.xyxy) > 0 and len(tubeResults.xyxy[0]) > 0:
            centerx, centery, depth = self.getTubeCoordinates(tubeResults, depth_frame)
            orientation = self.getTubeOrientation(color_frame, tubeResults, centerx, centery)
            return centerx, centery, depth, orientation
        return -1, -1, -1, -1

    def getTubeCoordinates(self, depth_frame, tubeResults):
        centery = int((tubeResults[0][0][1] + tubeResults[0][0][3]) / 2)
        centerx = int((tubeResults[0][0][0] + tubeResults[0][0][2]) / 2)
        depth = depth_frame.get_distance(centerx, centery) * 100
        return centerx, centery, depth

    def getTubeOrientation(self, color_frame, tubeResults, centerx, centery):
        xdist = (tubeResults[0][0][0] - tubeResults[0][0][2])
        ydist = (tubeResults[0][0][1] - tubeResults[0][0][3])
        ratio = xdist / ydist

        if ratio > 3:
            return 90
        elif ratio < .55:
            return 0
        
        color_image = np.asanyarray(color_frame.get_data())
        return int(edge.get_degrees(
                    (int(tubeResults[0][0][0]), int(tubeResults[0][0][1])),
                    (int(tubeResults[0][0][2]), int(tubeResults[0][0][3])),
                    (centerx, centery),
                    color_image)
                )
