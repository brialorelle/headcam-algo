import cv2
from mtcnn import face

"""
The FaceDetector class exposes two public members

self.name: the name of the detector

self.detect_faces: a method which, given an image as numpy array, returns a list of detected
faces as bounding boxes (x,y,w,h).
"""
class FaceDetector:
    def __init__(self,name):
        self.name = name
        self.__detector_lookup = {
            'vj' : self.vj_detect,
            'mtcnn' : self.mtcnn_detect
        }
        if self.name in self.__detector_lookup:
            self.detect_faces = self.__detector_lookup[self.name]
        else:
            raise ValueError('no detector with that name exists.')
        self.__detector_object = None
        self.__load_detector()

    def __load_detector(self):
        """
        Private member that loads the appropriate detector into self.DETECTOR_OBJECT.
        """
        if self.name == 'vj':
            #TODO: save absolute paths to detectors as constants
            self.__detector_object = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        elif self.name == 'mtcnn':
            self.__detector_object = face.Detection()
        else:
            pass

    def __vj_detect(self, img):
        """
        Private member for Viola-Jones face detection.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.__detector_object.detectMultiScale(gray, 1.3, 5)
        return faces

    def __mtcnn_detect(self, img):
        """
        Private member for MTCNN face detection.
        """
        return self.__detector_object.find_faces(img)
