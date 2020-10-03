from maven import Maven
import numpy as np
import ast
import multiprocessing as mp
import cv2
import random
from PIL import Image

from flask import Flask, request, jsonify
flaskserver = Flask(__name__)

num_classes = 94
thresh_conf = 0.2

global maven, athena

class Athena:
    ''' Class to hold member methods and variables
        for drawing detections. '''

    def __init__(self):
        ''' Method called when class object is created. '''

        self.path = 'classes.txt'
        self.classes = self.read_class_names(self.path)
        self.num_classes = len(self.classes)
        self.colors = self.colorGenerator(self.num_classes)

    def colorGenerator(self, num):
        ''' Method to generate random colors. '''

        colors = dict()
        for i in range(0, num):
            temp = list()
            b = random.randint(0, 255)
            g = random.randint(0, 255)
            r = random.randint(0, 255)
            temp.append(b)
            temp.append(g)
            temp.append(r)
            colors.update({i+1:temp})

        return colors

    def read_class_names(self, path):
        ''' Method to read the class names. '''
        try:
            names = dict()
            with open(path, 'r') as data:
                for ID, name in enumerate(data):
                    names[ID + 1] = name.strip('\n')
            data.close()
            return names

        except:
            print('Failed to read class names')
            traceback.print_exc()
            sys.exit(0)

    def colorGenerator(self, num):
        ''' Method to generate random colors. '''

        colors = dict()
        for i in range(0, num):
            temp = list()
            b = random.randint(0, 255)
            g = random.randint(0, 255)
            r = random.randint(0, 255)
            temp.append(b)
            temp.append(g)
            temp.append(r)
            colors.update({i+1:temp})

        return colors

    def read_class_names(self, path):
        ''' Method to read the class names. '''
        try:
            names = dict()
            with open(path, 'r') as data:
                for ID, name in enumerate(data):
                    names[ID + 1] = name.strip('\n')
            data.close()
            return names

        except:
            print('Failed to read class names')
            traceback.print_exc()
            sys.exit(0)

    def plotResults(self, frame, result):
        ''' Method to plot results. '''

        class_ids = result[0][0]
        confidence = result[0][1]
        boundaries = result[0][2]

        for counter in range(len(class_ids)):
            class_id = self.classes[class_ids[counter]]
            if(class_id == 'fire' or class_id == 'person'):
                conf = str(confidence[counter])
                x1 = int(boundaries[counter][0])
                y1 = int(boundaries[counter][1])
                x2 = int(boundaries[counter][2])
                y2 = int(boundaries[counter][3])
                color = self.colors[class_ids[counter]]
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.rectangle(frame, (x1, y1), (x1 + (len(class_id) + len(conf)) * 20,
                                y1 - 25) , color, -1, cv2.LINE_AA)
                cv2.putText(frame, class_id + ':' + conf, (x1, y1),
                            cv2.FONT_HERSHEY_COMPLEX, 0.85, (0, 0, 0), 1, cv2.LINE_AA)
        return frame

@flaskserver.route(rule='/detect_drone', methods=['POST'])
def detect_drone():
    ''' Method to perform detections and return the results. '''

    content = request

    data = ast.literal_eval(content.data.decode('utf-8'))

    # Parse the Data
    batch = data['Batch'] # Batch of Images
    batch_len = data['BatchLength'] # Length of Batch
    height = data['ImageHeight'] # Height of Image
    width = data['ImageWidth'] # Width of Image
    channels = data['Channels'] # Color Channels

    # Get batch in NumPy
    batch = np.fromstring(batch, np.uint8).reshape((batch_len, height, width, channels))

    results = maven.infer(batch)
    results_scrubbed = list()

    for result in results.keys():
        classes = list()
        bbox = list()
        confidence = list()
        for cat in range(1, num_classes + 1):
            for val in results[result][cat]:
                conf = val[4]
                if not conf > thresh_conf:
                    continue
                x1 = val[0]
                y1 = val[1]
                x2 = val[2]
                y2 = val[3]
                classes.append(cat)
                confidence.append(conf)
                bbox.append([x1, y1, x2, y2])
        results_scrubbed.append([classes, confidence, bbox])
    return jsonify({'Response':str(results_scrubbed)})

@flaskserver.route(rule='/detect', methods=['POST'])
def detect():
    ''' Method to perform detections and return the results. '''

    content = request

    img = Image.open(content.files['file'].stream)
    img = np.asarray(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Parse the Data
    batch = img.expand_dims(axis=0) # Batch of Images
    # batch_len = batch.shape[0]# Length of Batch
    # height = batch.shape[1] # Height of Image
    # width = batch.shape[2] # Width of Image
    # channels = batch.shape[3] # Color Channels

    # # Get batch in NumPy
    # batch = np.fromstring(batch, np.uint8).reshape((batch_len, height, width, channels))
    results = maven.infer(batch)
    results_scrubbed = list()

    for result in results.keys():
        classes = list()
        bbox = list()
        confidence = list()
        for cat in range(1, num_classes + 1):
            for val in results[result][cat]:
                conf = val[4]
                if not conf > thresh_conf:
                    continue
                x1 = val[0]
                y1 = val[1]
                x2 = val[2]
                y2 = val[3]
                classes.append(cat)
                confidence.append(conf)
                bbox.append([x1, y1, x2, y2])

        results_scrubbed.append([classes, confidence, bbox])
        frame = batch.squeeze()
        frame = athena.plotResults(frame, results_scrubbed)
        cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
        cv2.imshow('Result', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return jsonify({'Response':str(results_scrubbed)})

global maven, athena
maven = Maven()
athena = Athena()

if __name__ == '__main__':
    flaskserver.run(host='127.0.0.1',
                    port=5000,
                    debug=True)