import pandas as pd
import cv2

df = pd.read_csv('/scratch/users/agrawalk/cpu_mtcnn_test.csv',header=None)
df = df[df[2]]

def save_cropped(row):
    x, y, w, h = int(row[3]), int(row[4]), int(row[5]), int(row[6])
    num = '0' * (5 - len(str(row[1]))) + str(row[1])
    img = cv2.imread('/scratch/users/agrawalk/testvid_rotated/image-{}.jpg'.format(num))
    img = img[y:y+h,x:x+w]
    cv2.imwrite('/scratch/users/agrawalk/testcrop/crop_image-{}.jpg'.format(num), img)

df.apply(save_cropped, axis=1)
