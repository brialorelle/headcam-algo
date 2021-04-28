import os
import numpy as np
import pandas as pd

# load flattened numpy arrays per video, extracts bounding boxes for hands and faces
# per frame, and saves as long format CSV (one row per bounding box, maximum 9 per frame)

VID_PATH = "/scratch/groups/mcfrank/Home_Headcam_new/outputs/openpose_flattened/" 
OUT_PATH = "/scratch/groups/mcfrank/Home_Headcam_new/bounding_boxes/"
#VID_PATH = "openpose_flattened"
#f = "A_20130531_0818_01.npy" # for testing

frame_size = {'x':640, 'y':480} # pixels; keypoint x,y coords are normalized 0-1, but go out of frame occasionall
# min=-.22, max=1.16

files = os.listdir(VID_PATH)

# 130 for pose (18), face (70), L hand (21), and R hand (21) keypoints, in that order
# https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/02_output.md


def get_eye_distance(face_x, face_y, face_conf):
	pupil_left_X = face_x[68]
	pupil_right_X = face_x[69]
	pupil_dist = pupil_right_X - pupil_left_X # 0,0 is origin, so right-left
	if sum(face_conf)==0:
		pupil_dist=np.nan
	return pupil_dist

def is_full_face(face_x, face_y, face_conf, conf_thres):
	mouth = range(48,60) # range = n:n-1
	left_eye = range(36,42)
	right_eye = range(42,48)
	nose = range(27,36)
	mouth_conf = np.mean(face_conf[mouth])
	left_eye_conf = np.mean(face_conf[left_eye])
	right_eye_conf = np.mean(face_conf[right_eye])
	nose_conf = np.mean(face_conf[nose])
	full_face = (mouth_conf>conf_thres) & (left_eye_conf>conf_thres) & (right_eye_conf>conf_thres) & (nose_conf>conf_thres)
	return full_face

def get_all_bounding_boxes(vid_name,detection,i,p,conf_thres=0):
	# (X, Y, confidence) x 130 keypoints
	X = detection[0]
	Y = detection[1]
	conf = detection[2]
	# pose
	pose_x = X[:18]
	pose_y = Y[:18]
	pose_conf  = conf[:18]
	# face
	face_x = X[18:88]
	face_y = Y[18:88]
	face_conf = conf[18:88]
	# Lhand
	Lhand_x = X[88:109]
	Lhand_y = Y[88:109]
	Lhand_conf = conf[88:109]
	# Rhand
	Rhand_x = X[109:]
	Rhand_y = Y[109:]
	Rhand_conf = conf[109:]
	# only get keypoints above a certain confidence threshold
	pose_x = pose_x[pose_conf>conf_thres]
	pose_y = pose_y[pose_conf>conf_thres]
	face_x_all = face_x
	face_y_all = face_y
	face_x = face_x[face_conf>conf_thres]
	face_y = face_y[face_conf>conf_thres]
	Lhand_x = Lhand_x[Lhand_conf>conf_thres]
	Lhand_y = Lhand_y[Lhand_conf>conf_thres]
	Rhand_x = Rhand_x[Rhand_conf>conf_thres]
	Rhand_y = Rhand_y[Rhand_conf>conf_thres]
	# extra face information
	full_face = is_full_face(face_x_all, face_y_all, face_conf, conf_thres)
	eye_distance = get_eye_distance(face_x_all, face_y_all, face_conf)
	# get average conf of included points
	pose_conf_mean = np.mean(pose_conf[pose_conf>conf_thres])
	face_conf_mean = np.mean(face_conf[face_conf>conf_thres])
	Lhand_conf_mean = np.mean(Lhand_conf[Lhand_conf>conf_thres])
	Rhand_conf_mean = np.mean(Rhand_conf[Rhand_conf>conf_thres])
	# outputs
	pose = [vid_name, i, p, "pose", conf_thres] + get_bounding_box(pose_x, pose_y, pose_conf_mean) + [np.nan, np.nan]
	face = [vid_name, i, p, "face",conf_thres] + get_bounding_box(face_x, face_y, face_conf_mean) + [eye_distance, full_face]
	rhand = [vid_name,i, p, "hand",conf_thres] + get_bounding_box(Rhand_x, Rhand_y, Rhand_conf_mean) + [np.nan, np.nan]
	lhand = [vid_name,i, p, "hand",conf_thres] + get_bounding_box(Lhand_x, Lhand_y, Lhand_conf_mean) + [np.nan, np.nan]
	return pose, face, rhand, lhand 

def get_bounding_box(X, Y, conf_mean):
	if np.isnan(conf_mean):
		return [np.nan, np.nan, np.nan, np.nan]
	left = np.min(X)
	top = np.min(Y) # (0,0) is top left
	height = np.max(Y) - top
	width = np.max(X) - left
	return [height, width, left, top, conf_mean]


processed = os.listdir(OUT_PATH) # skip these
# labels for big dataframe
col_names = ["vid_name","frame", "person", "label", "conf_thres","height", "width", "left", "top", "mean_confidence", "eye_distance", "full_face"]
high_conf_thres=.5

# look into these:
#  Problem processing A_20140609_2027_02
#  Problem processing A_20130607_0825_01

# f = "S_20140717_2100_05.npy"

# A_20130721_1008_02.npy - array.shape = shape
# ValueError: cannot reshape array of size 105207808 into shape (53953,5,3,130)

# A_20130721_1008_02.npy
# ValueError: cannot reshape array of size 105207808 into shape (53953,5,3,130)

# Problem processing A_20130721_1008_02

for f in files:
	df = [] # list of bounding boxes
	df_hc = [] # list of high confidence bounding boxes
	vid_name = f.strip(".npy")
	if not os.path.exists(OUT_PATH + vid_name + "_bounding_boxes.csv"):
		try:
			v = np.load(os.path.join(VID_PATH, f)) # frames x people (3) x keypoint (X, Y, confidence) x 130
			for i in range(v.shape[0]): # frame i
				detection = False # save a blank row if there are no detections for this frame
				for p in range(v.shape[1]): # person p
					if np.sum(v[i][p][2])>0: # 0 confidence = no detection
						detection = True
						# Error: this_detection not defined, GK substituted v[i][p]
						pose, face, rhand, lhand = get_all_bounding_boxes(vid_name,v[i][p],i,p,0)  # all detections
						pose_h, face_h, rhand_h, lhand_h = get_all_bounding_boxes(vid_name,v[i][p],i,p,.5)  # high confidence detections
						# append all bbs
						df.append(pose)
						if ~np.isnan(face[8]): # 8th column = mean confidence (as outputted by get_all_bounding_boxes)
							df.append(face)
						if ~np.isnan(rhand[8]):
							df.append(rhand)
						if ~np.isnan(lhand[8]):
							df.append(lhand)
						# append high confidence bbs
						df_hc.append(pose_h)
						if ~np.isnan(face_h[8]):
							df_hc.append(face_h)
						if ~np.isnan(rhand_h[8]):
							df_hc.append(rhand_h)
						if ~np.isnan(lhand_h[8]):
							df_hc.append(lhand)
				# add a row indicating no detection for that frame (makes the file much larger)
				if not detection:
					df.append([vid_name, i, np.nan, 'none', np.nan,np.nan, np.nan,np.nan,np.nan,np.nan,np.nan, np.nan])
					df_hc.append([vid_name, i, np.nan, 'none', np.nan,np.nan, np.nan,np.nan,np.nan,np.nan,np.nan, np.nan])
			# write out dataframes
			df = pd.DataFrame(df)
			df.columns = col_names
			df.fillna('') # replace NaNs with emptiness
			df.to_csv(os.path.join(OUT_PATH, vid_name+"_bounding_boxes.csv"), index=False)
			# and for high confidence
			df_hc = pd.DataFrame(df_hc)
			df_hc.columns = col_names
			df_hc.fillna('') # replace NaNs with emptiness
			df_hc.to_csv(os.path.join(OUT_PATH, vid_name+"_bounding_boxes_high_conf.csv"), index=False)
		except:
			print("Problem processing "+vid_name)

