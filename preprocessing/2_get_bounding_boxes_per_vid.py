import os
import numpy as np
import pandas as pd

# load flattened numpy arrays per video, extracts bounding boxes for hands and faces
# per frame, and saves as long format CSV (one row per bounding box, maximum 9 per frame)

VID_PATH = "/scratch/groups/mcfrank/Home_Headcam_new/openpose_flattened_whole" # /scratch/groups/mcfrank/Home_Headcam_new/openpose_flattened_whole
OUT_PATH = "/scratch/groups/mcfrank/Home_Headcam_new/bounding_boxes/"
#VID_PATH = "openpose_flattened"
#f = "A_20130531_0818_01.npy" # for testing

frame_size = {'x':640, 'y':480} # pixels; keypoint x,y coords are normalized 0-1, but go out of frame occasionall
# min=-.22, max=1.16

files = os.listdir(VID_PATH)

# 130 for pose (18), face (70), L hand (21), and R hand (21) keypoints, in that order

def get_bounding_box(X, Y):
	left = np.min(X)
	top = np.min(Y) # (0,0) is top left
	height = np.max(Y) - top
	width = np.max(X) - left
	return([height, width, left, top])

def get_face_hand_bounding_boxes(detection):
	# (X, Y, confidence) x 130 keypoints
	X = detection[0]
	Y = detection[1]
	conf = detection[2]
	pose_x = X[:18]
	pose_y = Y[:18]
	face_x = X[18:88]
	face_y = Y[18:88]
	Lhand_x = X[88:109]
	Lhand_y = Y[88:109]
	Rhand_x = X[109:]
	Rhand_y = Y[109:]
	bbs = [get_bounding_box(pose_x, pose_y) + [np.mean(conf[:18])], 
		get_bounding_box(face_x, face_y) + [np.mean(conf[18:88])], 
		get_bounding_box(Lhand_x, Lhand_y) + [np.mean(conf[88:109])], 
		get_bounding_box(Rhand_x, Rhand_y) + [np.mean(conf[109:])]]
	return bbs # could add mean confidences for face and each hand
	# return height, width, left, top

col_names = ["frame", "person", "label", "height", "width", "left", "top", "mean_confidence"]

processed = os.listdir(OUT_PATH) # skip these

# look into these:
#  Problem processing A_20140609_2027_02
#  Problem processing A_20130607_0825_01

for f in files:
	df = [] # list of bounding boxes
	vid_name = f.strip(".npy")
	if not os.path.exists(OUT_PATH + vid_name + "_bounding_boxes.csv"):
		try:
			v = np.load(os.path.join(VID_PATH, f)) # frames x people (3) x keypoint (X, Y, confidence) x 130
			for i in range(v.shape[0]): # frame i
				detection = False # save a blank row if there are no detections for this frame
				for p in range(3): # person p
					if np.sum(v[i][p][2])>0: # 0 confidence = no detection
						detection = True
						bbs = get_face_hand_bounding_boxes(v[i][p]) # [face, Lhand, Rhand]
						#for bb in bbs:
						df.append([i, p, "pose"] + bbs[0])
						df.append([i, p, "face"] + bbs[1])
						df.append([i, p, "hand"] + bbs[2])
						df.append([i, p, "hand"] + bbs[3])
				# add a row indicating no detection for that frame (makes the file much larger)
				#if not detection:
				#	df.append([i, -1,-1,  -1,-1,-1,-1,-1])
			df = pd.DataFrame(df)
			df.columns = col_names
			df.to_csv(OUT_PATH + vid_name+"_bounding_boxes.csv")
		except:
			print("Problem processing "+vid_name)

