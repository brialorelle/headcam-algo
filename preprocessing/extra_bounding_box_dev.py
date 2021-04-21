import numpy as np
import pandas as pd
from openpose_helpers import recover_npy
import os
​
test_file =  '/Users/brialong/Documents/GitHub/headcam-algo/data/test_data/A_20130609_0827_04.json'
vid_df = pd.read_json(open(test_file, 'r'))
v = recover_npy(vid_df)
​
def get_bounding_box(X, Y, conf):
	if np.sum(conf)==0:
		return [np.nan, np.nan, np.nan, np.nan]
	left = np.min(X)
	top = np.min(Y) # (0,0) is top left
	height = np.max(Y) - top
	width = np.max(X) - left
	return [height, width, left, top, conf]

def get_eye_distance(face_x, face_y, face_conf):
	pupil_left_X = face_x[68]
	pupil_right_X = face_x[69]
	pupil_dist = pupil_right_X - pupil_left_X # 0,0 is origin, so right-left
	if sum(face_conf)==0:
		pupil_dist=np.nan
	return pupil_dist

def is_full_face(face_x, face_y, face_conf, conf_thres):
	mouth = range(48,59)
	left_eye = range(36,40)
	right_eye = range(42,47)
	mouth_conf = np.mean(face_conf[mouth])
	left_eye_conf = np.mean(face_conf[left_eye])
	right_eye_conf = np.mean(face_conf[right_eye])
	full_face = (mouth_conf>conf_thres) & (left_eye_conf>conf_thres) & (right_eye_conf>conf_thres)
	return full_face

def get_face_info(detection, conf_thres):
	X = detection[0]
	Y = detection[1]
	conf = detection[2]
	face_x = X[18:88]
	face_y = Y[18:88]
	face_conf = conf[18:88]
	face_bb = get_bounding_box(face_x, face_y, np.mean(face_conf))
	full_face = is_full_face(face_x, face_y, face_conf, conf_thres)
	eye_distance = get_eye_distance(face_x, face_y, face_conf)
	face_info = [face_bb, full_face, eye_distance]
	return face_info

def get_face_hand_bounding_boxes(detection):
	# (X, Y, confidence) x 130 keypoints
	X = detection[0]
	Y = detection[1]
	conf = detection[2]
	pose_x = X[:18]
	pose_y = Y[:18]
	face_x = X[18:88]
	face_y = Y[18:88]
	face_conf = conf[18:88]
	Lhand_x = X[88:109]
	Lhand_y = Y[88:109]
	Rhand_x = X[109:]
	Rhand_y = Y[109:]
	# only get keypoints with >0 confidence for pose
	pose_conf  = conf[:18]
	pose_x = pose_x[pose_conf>0]
	pose_y = pose_y[pose_conf>0]
	pose_conf_mean = np.mean(conf[:18])
	face_conf_mean = np.mean(conf[18:88])
	Lhand_conf_mean = np.mean(conf[88:109])
	lhand_min_conf = np.min(conf[88:109])
	lhand_max_conf = np.max(conf[88:109])
	Rhand_conf_mean = np.mean(conf[109:])
	# face/hands never had non-zero confidence pose if they are detected....
	# print('face conf = {}, num face_x zeros = {}'.format(face_conf_mean, sum(face_x==0)))
	# print('Lhand_conf_mean conf = {}, num Lhand_x zeros = {}, min_conf = {}, max_conf = {}'.format(Lhand_conf_mean, sum(Lhand_x==0),lhand_min_conf,lhand_max_conf))
	bbs = [get_bounding_box(pose_x, pose_y, pose_conf_mean), 
		get_bounding_box(face_x, face_y, face_conf_mean), 
		get_bounding_box(Lhand_x, Lhand_y, Lhand_conf_mean), 
		get_bounding_box(Rhand_x, Rhand_y, Rhand_conf_mean) ]
	return bbs # could add mean confidences for face and each hand
	# return height, width, left, top

col_names = ["frame", "person", "label", "height", "width", "left", "top", "mean_confidence"]
col_names_faces = ["frame","person","height","width","left",'"top',"is_full_face","eye_distance"]

## try this out on frames from one video
df=[]
df_faces=[]
conf_thres=.1
for i in range(v.shape[0]):
	for p in range(v.shape[1]): # person p
		if np.sum(v[i][p][2])>0: # 0 confidenpce = no detection
			detection = True
			bbs = get_face_hand_bounding_boxes(v[i][p]) # [face, Lhand, Rhand]
			#for bb in bbs:
			# df.append([i, p, "pose"] + bbs[0])
			# df.append([i, p, "face"] + bbs[1])
			# df.append([i, p, "hand"] + bbs[2])
			# df.append([i, p, "hand"] + bbs[3])
			if ~np.isnan(bbs[1][1]): # if there was a face
				detection = v[i][p]
				face_info = get_face_info(detection, conf_thres)
				df_faces.append([i,p,face_info])

df_faces = pd.DataFrame(df_faces)
df_faces.columns = col_names_faces
		
	
# 
i=111
p=0
detection

## Frames for testing
# for a pose
i=54016
p=1

# for a face
i=53993
p=0
detection=v[i][p]
conf_thres = .1 ???
get_face_info(detection,conf_thres)

# for a l hand
i=7410
p=0
detection = v[i][p]
bbs = get_face_hand_bounding_boxes(v[i][p])


