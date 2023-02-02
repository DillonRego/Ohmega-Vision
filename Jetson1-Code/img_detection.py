import cv2
import torch
import os

path = '/home/herbie/OVision2022/yolov5/testTube_images/'
imgs = []
# Model
model = torch.hub.load('/home/herbie/OVision2022/yolov5', 'custom', path='best.pt', source='local')

# Image
#img = 'testTubes.JPG'  # or file, Path, PIL, OpenCV, numpy, list

for img_name in os.listdir(path):
    if img_name.endswith('.JPG'):
        img_name = 'testTube_images/' + img_name
        imgs.append(img_name)

# Inference
#results = model(img)
results = model(imgs)

# Results
results.save(save_dir='results/detection')
print(results)

