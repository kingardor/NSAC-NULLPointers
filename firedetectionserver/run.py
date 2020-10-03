import time
import numpy as np
import cv2
import sys
import requests
from videocaptureasync import VideoCaptureAsync
import traceback
import ast
import random
import sys

class Theia:
    ''' Class to hold member methods and variables
        for performing Inference. '''

    def __init__(self):
        ''' Method called when class object is created. '''

        self.path = 'src/classes.txt'
        self.classes = self.read_class_names(self.path)
        self.num_classes = len(self.classes)
        self.colors = self.colorGenerator(self.num_classes)
        self.inference_endpoint = 'http://127.0.0.1:8000/detect_drone'
        self.source_path = sys.argv[1]
        # self.source = VideoCaptureAsync(0 if self.source_path == 'webcam' else self.source_path,
        #                                 width=1920, height=1080)
        # self.source.start()
        self.source = cv2.VideoCapture(self.source_path)

        if len(sys.argv) > 2 and sys.argv[2] == '--record':
            ret, frame = self.source.read()
            if ret:
                height, width = frame.shape[0], frame.shape[1]
                self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.out = cv2.VideoWriter('output.avi',self.fourcc, 30.0, (width, height))

        cv2.namedWindow('Result', cv2.WINDOW_NORMAL)

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

    def inference(self):
        ''' Method to perform inference. '''

        while True:
            ret, frame = self.source.read()
            if ret:
                batch = np.expand_dims(frame, axis=0)
                batch_len, height, width, channels = batch.shape[0], batch.shape[1], batch.shape[2], batch.shape[3]

                data = dict()
                data.update({'Batch':batch.tostring()})
                data.update({'BatchLength':batch_len})
                data.update({'ImageHeight':height})
                data.update({'ImageWidth':width})
                data.update({'Channels':channels})

                response = requests.post(self.inference_endpoint, data=str(data))
                result = ast.literal_eval(ast.literal_eval(response.content.decode('utf-8'))['Response'])
                frame = self.plotResults(frame, result)
                if len(sys.argv) > 2 and sys.argv[2] == '--record':
                    self.out.write(frame)
                cv2.imshow('Result', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if len(sys.argv) > 2 and sys.argv[2] == '--record':
            self.out.release()
        # self.source.stop()
        self.source.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    print('Python: ', sys.version)
    print('OpenCV: ', cv2.__version__)
    print('Numpy: ', np.__version__)
    # print('CPU Core Count: ', cpu_count())
    # print('Available Multiprocessing Modes: ' ,get_all_start_methods())
    # print('Selected Multiprocessing Mode: ' ,get_start_method())
    print('-------------------------------------------------------')

    theia = Theia()
    theia.inference()