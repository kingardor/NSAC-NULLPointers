from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from maven import Maven
import _init_paths

import os
import numpy as np
import cv2
import read_classes
from opts import opts
from detectors.ctdet import CtdetDetector

image_ext = ['jpg', 'jpeg', 'png', 'webp']
video_ext = ['mp4', 'mov', 'avi', 'mkv']
time_stats = ['tot', 'load', 'pre', 'net', 'dec', 'post', 'merge']
num_classes = 94
maven = Maven()


def annotate(image_name, results):
    # Temp fix; 1 indicates the id of the image in the batch; the keys vary from 1 to batch_size
    results = results[1]

    # Annotation file name
    image = cv2.imread(image_name)
    annotation_file = image_name[:image_name.rfind('.')] + '.txt'
    handle = open(annotation_file, 'a+')
    num_classes, class_names = read_classes.get_class_details()

    classes_dict = {v: k+1 for k, v in enumerate(class_names)}
    line = ''
    for j in results.keys():
        # j_new = proper[current[j]]

        for bbox in results[j]:
            # print(j,  bbox[4])
            if bbox[4] >= 0.3 and j >= 87:
                category = j - 1
                bbox = np.array(bbox, dtype=np.int32)
                c_x = (bbox[0] + bbox[2]) / (2 * image.shape[1])
                c_y = (bbox[1] + bbox[3]) / (2 * image.shape[0])
                width = (bbox[2] - bbox[0]) / (image.shape[1])
                height = (bbox[3] - bbox[1]) / (image.shape[0])
                line += '{} {} {} {} {}\n'.format(
                    category, c_x, c_y, width, height)
                # print("image: ", image_name, j_new, category)
                # Write data
    handle.write(line)
    # print("="*20)
    handle.close()
    return


def demo(opt):
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpus_str
    opt.debug = max(opt.debug, 1)
    detector = CtdetDetector(opt)

    if opt.demo == 'webcam' or \
            opt.demo[opt.demo.rfind('.') + 1:].lower() in video_ext:
        cam = cv2.VideoCapture(0 if opt.demo == 'webcam' else opt.demo)

        detector.pause = False
        while True:
            _, img = cam.read()
            cv2.imshow('input', img)
            ret = detector.run(img)
            time_str = ''
            for stat in time_stats:
                time_str = time_str + '{} {:.3f}s |'.format(stat, ret[stat])
            if cv2.waitKey(1) == 27:
                return  # esc to quit
    else:
        if os.path.isdir(opt.demo):
            image_names = []
            ls = os.listdir(opt.demo)
            for file_name in sorted(ls):
                ext = file_name[file_name.rfind('.') + 1:].lower()
                if ext in image_ext:
                    image_names.append(os.path.join(opt.demo, file_name))
        else:
            image_names = [opt.demo]

        for (image_name) in image_names:
            # ret = detector.run(image_name)
            ret = maven.infer(image_name)
            annotate(image_name, ret['results'])
            time_str = ''
            for stat in time_stats:
                time_str = time_str + '{} {:.3f}s |'.format(stat, ret[stat])
            # print(time_str)


if __name__ == '__main__':
    opt = opts().init()
    demo(opt)
