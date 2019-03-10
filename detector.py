import numpy as np
import cv2
import mtcnn.face

"""
The FaceDetector class exposes two public members

self.name: the name of the detector used under the hood (currently allowed: "vj" or "mtcnn")

self.detect_faces: a method which, given an image as numpy array, returns a numpy array of detected
faces as bounding boxes [x,y,w,h].
"""

class FaceDetector:
    def __init__(self,name):
        self.name = name
        self.__detector_lookup = {
            'vj' : self.__vj_detect,
            'mtcnn' : self.__mtcnn_detect
        }
        if self.name in self.__detector_lookup:
            self.detect_faces = self.__detector_lookup[self.name]
        else:
            raise ValueError('no detector with that name exists.')
        self.__detector_object = None
        self.__load_detector()

    def __load_detector(self):
        """
        Private member that loads the appropriate detector into self.__detector_object.
        """
        if self.name == 'vj':
            #TODO: save absolute paths to detectors as constants
            self.__detector_object = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        elif self.name == 'mtcnn':
            self.__detector_object = mtcnn.face.Detection()
        else:
            pass

    def __vj_detect(self, img):
        """
        Private member for Viola-Jones face detection.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.__detector_object.detectMultiScale(gray, 1.3, 5)
        return list(faces)

    def __mtcnn_detect(self, img):
        """
        Private member for MTCNN face detection.
        """
        faces =  self.__detector_object.find_faces(img)
        faces = [face.bounding_box for face in faces]

        #convert x1,y1,x2,y2 to x,y,w,h format
        faces = [np.array([bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]]) for bb in faces]
        return faces
