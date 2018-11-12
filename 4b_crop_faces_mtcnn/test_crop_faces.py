import pandas as pd
import cv2

df = pd.read_csv('cpu_mtcnn_test.csv',header=None)
df = df[df[2] == True] # gets the slice of the dataframe where Face detected is true

def save_cropped(row): # for each face-detected frame, saves the bounding box as an image
    x, y, w, h = int(row[3]), int(row[4]), int(row[5]), int(row[6])
    num = '0' * (5 - len(str(row[1]))) + str(row[1])
    img = cv2.imread('testvid_rotated/image-{}.jpg'.format(num)) 
    #this is assuming you have the rotated frames directory in this directory
    img = img[y:y+h,x:x+w]
    cv2.imwrite('testcrop/cropped_image-{}.jpg'.format(num), img)

df.apply(save_cropped, axis=1)
