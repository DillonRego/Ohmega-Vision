import tensorflow as tf
from google.protobuf import text_format

with open('ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt') as f:
    txt = f.read()
gdef = text_format.Parse(txt, tf.compat.v1.GraphDef())
tf.io.write_graph(gdef, '.', 'model.pb', as_text=False)
