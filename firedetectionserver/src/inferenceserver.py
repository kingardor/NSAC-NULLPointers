from maven import Maven
import numpy as np
import ast
import multiprocessing as mp

from flask import Flask, request, jsonify
flaskserver = Flask(__name__)

num_classes = 94
thresh_conf = 0.2

maven = Maven()

@flaskserver.route(rule='/detect', methods=['POST'])
def detect():
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

if __name__ == '__main__':
    flaskserver.run(host='127.0.0.1',
                    port=5000,
                    debug=True)