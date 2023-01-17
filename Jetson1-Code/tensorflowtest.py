import pyrealsense2 as rs
import numpy as np
import cv2
import tensorflow as tf 

# Load tensorflow module into memory
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.compat.v1.gfile.GFile(faster_rcnn_inception_v2_coco_2018_01_28.pb, 'rb') as fid:
        seralized_graph = fid.read()
        od_graph_def.ParseFromString(seralized_graph)
        tf.compat.v1.import_graph_def(od_graph_def, nam='')
    sess = tf.compat.v1.Session(graph=detection_graph)

# initialize input and output vectors
# input is image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
# output are boxes, scores, classes
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
# score represents level of confidence with object
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

num_detections = detection_graph.get_tensor_by_name('num_detections:0')
