require(stringr)

# should run on master_frames_openpose.h5, but for now use gold set
frame_size = c(640,480) # pixels; keypoint x,y coords are normalized 0-1, but go out of frame occasionally
# min=-.22, max=1.16
load("ketan_gold_sample.RData") 

# bounding box should be x1 = min(x), y1=min(y), x2=max(x), y2=max(x)

ketan_gold$face_openpose
ketan_gold$face_keypoints
ketan_gold$hand_left_keypoints
ketan_gold$hand_left_keypoints

# what are "face_keypoints_tuple"  and "pose_keypoints_tuple" ?

table(ketan_gold$hand_openpose, ketan_gold$hand_openpose_wrist)


face_inds <- which(ketan_gold$face_openpose==1)
#fd <- ketan_gold[face_inds,] # or do on all -- no keypoints = "[]"

#fd$face_keys <- vapply(fd$face_keypoints, paste, collapse = ", ", character(1L))

all = list(dat=ketan_gold)

get_hand_keypoints <- function(all, hand="left") {
  hd = all$dat
  col_kp = paste0("hand_",hand,"_keypoints")
  col_num = paste0("num_",hand,"_hands")
  #hd$hand_keys = NA
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
      if(length(vals) > 63) {
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
  fd$face_keys = NA
  fd$face_keypoints = gsub("\\[|\\]", "", fd$face_keypoints) # removes all left or right brackets
  fd$num_faces = NA
  fkp = list()
  for(i in 1:nrow(fd)) {
    # if there are multiple people, these are of the form [[1,2,..,210], [211,212,..,421], ..]
    if(str_length(fd[i,col_kp])==0) {
      fd[i,]$num_faces = 0
    } else {
      vals = eval(parse(text=paste('c(',fd[i,]$face_keypoints,')')))
      if(length(vals) > 210) {
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
save(all, file="hand_face_keypoints.RData")

# drop pose_keypoints_tuple, face_keypoints_tuple, pose_keypoints, 

hist(c(all$dat$num_left_hands, all$dat$num_right_hands))
hist(all$dat$num_faces)

