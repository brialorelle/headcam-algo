require(stringr)

# should run on master_frames_openpose.h5, but for now use gold set
frame_size = list(x=640, y=480) # pixels; keypoint x,y coords are normalized 0-1, but go out of frame occasionally
# min=-.22, max=1.16
load("ketan_gold_sample.RData") # in headcam-algo/analysis, maybe should be in /src/data/

# "face_keypoints_tuple"  and "pose_keypoints_tuple" include surrounding frames

#table(ketan_gold$hand_openpose, ketan_gold$hand_openpose_wrist)


face_inds <- which(ketan_gold$face_openpose==1)
#fd <- ketan_gold[face_inds,] # or do on all -- no keypoints = "[]"

#fd$face_keys <- vapply(fd$face_keypoints, paste, collapse = ", ", character(1L))

all = list(dat=ketan_gold)

get_hand_keypoints <- function(all, hand="left") {
  hd = all$dat
  col_kp = paste0("hand_",hand,"_keypoints")
  col_num = paste0("num_",hand,"_hands")
  hd[,col_kp] = gsub("\\[|\\]", "", hd[,col_kp]) # removes all left or right brackets
  hd[,col_num] = NA
  hkp = list()
  for(i in 1:nrow(hd)) {
    # no keypoints="[]", but what does it mean if all the keypoints are 0 ??
    if(str_length(hd[i,col_kp])==0) {
      hd[i,col_num] = 0
    } else {
      # if there are multiple people, these are of the form [[1,2,..,63], [64,65,..,127], ..]
      vals = eval(parse(text=paste('c(',hd[i,col_kp],')')))
      if(length(vals) >= 63) {
        num_hands = length(vals)/63
        hd[i,col_num] = num_hands
        #print(paste(num_hands, "hands found"))
        ll = list()
        for(h in 1:num_hands) {
          startind = 63*(h-1)+1
          endind = 63*h
          ll[[h]] = vals[startind:endind]
        }
      } else {
        ll = list(vals)
      }
      hkp[[i]] = ll
    }
  }
  all$dat = hd
  all[[paste0(hand,"_keys")]] = hkp
  return(all)
}


get_face_keypoints <- function(all) {
  fd = all$dat
  fd$face_keypoints = gsub("\\[|\\]", "", fd$face_keypoints) # removes all left or right brackets
  fd$num_faces = NA
  fkp = list()
  for(i in 1:nrow(fd)) {
    # if there are multiple people, these are of the form [[1,2,..,210], [211,212,..,421], ..]
    if(str_length(fd[i,col_kp])==0) {
      fd[i,]$num_faces = 0
    } else {
      vals = eval(parse(text=paste('c(',fd[i,]$face_keypoints,')')))
      if(length(vals) >= 210) {
        num_faces = length(vals)/210
        fd[i,]$num_faces = num_faces
        print(paste(num_faces, "faces found"))
        ll = list()
        for(f in 1:num_faces) {
          startind = 210*(f-1)+1
          endind = 210*f
          ll[[f]] = vals[startind:endind]
        }
      } else {
        ll = list(vals)
      }
      fkp[[i]] = ll
    }
  }
  #list(dat=fd, face_keys=fkp)
  all$dat = fd
  all$face_keys = fkp
  return(all)
}

all <- get_hand_keypoints(all, "left")
all <- get_hand_keypoints(all, "right")
all <- get_face_keypoints(all)
all$dat$pose_keypoints_tuple = NULL
all$dat$face_keypoints_tuple = NULL
all$dat$pose_keypoints = NULL
all$dat$hand_left_keypoints = NULL
all$dat$hand_right_keypoints = NULL
all$dat$face_keypoints = NULL
save(all, file="hand_face_keypoints.RData")

# drop pose_keypoints_tuple, face_keypoints_tuple, pose_keypoints, 

hist(c(all$dat$num_left_hands, all$dat$num_right_hands))
hist(all$dat$num_faces)


parse_keypoints <- function(v) {
  # e.g., |v| = 63 or 210 and form c(x1,y1,conf1, x2,y2,conf2, ...)
  inds = 1:length(v) %% 3
  x = v[which(inds==1)]
  y = v[which(inds==2)]
  conf = v[which(inds==0)]
  return(list(x=x, y=y, conf=conf))
}

# ToDo rescale to pixel values
get_bounding_box <- function(kp) {
  # kp = list(x, y, conf)
  # return height, width, left, top
  left = min(kp$x)
  top = max(kp$y) # is (0,0) top or bottom left? assume bottom left for now -- check python
  height = top - min(kp$y)
  width = max(kp$x) - left
  # these are still scaled - should rescale to pixels with frame_size$x and $y
  return(data.frame(height=height, width=width, left=left, top=top))
}


# ideally return dataframe with 1 row per face / hand BB
get_bounding_boxes <- function(all) {
  all$dat$vid_name = as.character(all$dat$vid_name)
  bbs = data.frame()
  # for each frame in all$dat, loop over any detections in
  for(i in 1:nrow(all$dat)) {
    tmp = all$dat[i,] # index, level_0?
    tr_info = tmp[,c("X","vid_name","frame","num_right_hands","num_left_hands","num_faces",
                     "hand_present","face_present","face_openpose","hand_openpose")] 
    # "hand_openpose_wrist" / "faceopenpose_nose"
    
    # extract height, width, left, top
    if(tmp$num_left_hands>0) {
      kps = all$left_keys[[i]]
      for(k in 1:length(kps)) {
        kp = parse_keypoints(kps[[k]])
        bb = get_bounding_box(kp)
        bb$label = "hand"
        bb$mean_conf = mean(kp$conf)
        bbs = rbind(bbs, cbind(tr_info, bb))
      }
    }
    
    if(tmp$num_right_hands>0) {
      kps = all$right_keys[[i]]
      for(k in 1:length(kps)) {
        kp = parse_keypoints(kps[[k]])
        bb = get_bounding_box(kp)
        bb$label = "hand"
        bb$mean_conf = mean(kp$conf)
        bbs = rbind(bbs, cbind(tr_info, bb))
      }
    }
    
    if(tmp$num_faces>0) {
      kps = all$face_keys[[i]]
      for(k in 1:length(kps)) {
        kp = parse_keypoints(kps[[k]])
        bb = get_bounding_box(kp)
        bb$label = "face"
        bb$mean_conf = mean(kp$conf)
        bbs = rbind(bbs, cbind(tr_info, bb))
      }
    }
    
  }
  bbs$WorkerID = 'OP' # OpenPose
  return(bbs)
}


bbs = get_bounding_boxes(all)
write.csv(bbs, file="gold_sample_bounding_boxes.csv", row.names=F)

# did we get them all?
total_detected_hands_faces = sum(all$dat$num_faces) + sum(all$dat$num_left_hands) + sum(all$dat$num_right_hands)
nrow(bbs) == total_detected_hands_faces
