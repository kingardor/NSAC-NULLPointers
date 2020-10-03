from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths

import numpy as np
import cv2
import pickle
import matplotlib.pyplot as plt
from opts import opts
from detectors.ctdet import CtdetDetector
import time

# For Kafka
from confluent_kafka import Producer, Consumer, KafkaError

# For Kafka Topics
from args import frames_topic, inference_topic

# Runtime parameters
from args import num_classes, thresh_conf

class Zeus:
    ''' Class to hold methods and variables for Inference. '''
    
    def __init__(self):
        ''' Method called when object of class is created. '''
        
        # Initialize Result Topic Consumer
        self.frames_consumer = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'cameras',
            'auto.offset.reset': 'earliest'
        })
        self.frames_consumer.subscribe([frames_topic])

        # Initialize Frames Topic Producer
        self.inference_producer = Producer({'bootstrap.servers': 'localhost:9092',
                                             'message.max.bytes': '10000000'})
        
        # Get options
        self.opt = opts().init()
        self.opt.debug = max(self.opt.debug, 1)

        # Instantiate the Model
        self.detector = CtdetDetector(self.opt)
    
    def delivery_report(self, err, msg):
        ''' Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). '''
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            pass

    def infer(self):
        ''' Method to share inferred knowledge '''
        
        print('Ready for Inference!')
        start = 0
        while True:
            start = time.time()
            
            self.inference_producer.poll(0)
            
            data = self.frames_consumer.poll()
            if data is None:
                time.sleep(0.01)
                continue
            if data.error():
                print("Consumer error: {}".format(data.error()))
                continue
            
            data = pickle.loads(data.value())
            # Parse the Data
            batch = data['Batch'] # Batch of Images
            batch_len = data['BatchLength'] # Length of Batch
            height = data['ImageHeight'] # Height of Image
            width = data['ImageWidth'] # Width of Image
            channels = data['Channels'] # Color Channels
            
            # Get batch in NumPy ndarray
            # batch = np.fromstring(batch, np.uint8).reshape((batch_len, height, width, channels))
            
            # Perform Inference
            results = self.detector.run(batch)
            results = results['results']

            # Cleanse the result
            
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
            
            data = dict()
            data.update({'Batch':batch})
            data.update({'BatchLength':batch_len})
            data.update({'ImageHeight':height})
            data.update({'ImageWidth':width})
            data.update({'Channels':channels})
            data.update({'Results':results_scrubbed})
            
            self.inference_producer.produce(inference_topic, pickle.dumps(data), callback=self.delivery_report)
            self.inference_producer.flush()

            print(time.time() - start, end='\r')
        
        self.frames_consumer.close()
if __name__ == '__main__':
    zeus = Zeus()
    zeus.infer()
    
    