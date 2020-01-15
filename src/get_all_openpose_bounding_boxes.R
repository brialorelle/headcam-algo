
# load bounding boxes from openpose detections from the entire dataset
# (created in get_bounding_boxes_per_vid.py using numpy vectors in $GROUP_SCRATCH/openpose_flattened_whole)

require(data.table)
require(here)
require(stringr)

files <- list.files("../src/bounding_boxes") # 1632 vids
# A_20140630_2117_04_bounding_boxes.csv had no detections

load("../src/data/vid_info.RData") # vid_info
downup = fread("../src/data/video_right-side-up.csv", stringsAsFactors = F)

df <- data.frame()

#had to specify columns to get rid of the total column
for (i in 1:length(files)) {
  tmp <- fread(paste("../src/bounding_boxes", files[i], sep='/'), stringsAsFactors = F) 
  if(ncol(tmp)==9) {
    tmp$V1 = NULL
    this_vid = str_remove(files[i], "_bounding_boxes.csv")
    tmp$child_id = strsplit(files[i], '_')[[1]][1]
    tmp$vid_name = this_vid
    tmp$age_days = vid_info[which(vid_info$vid_name == this_vid)[1],]$age_days
    tmp$right_side_up = downup[which(downup$video == this_vid),]$right_side_up
    # remove any rows with all 0 bounding box + confidences (~50%)
    tmp = subset(tmp, mean_confidence!=0)
    #df <- rbindlist(list(df, tmp)) # , use.names = T
    df = rbind(df, tmp)
  } else {
    print(paste("check file: ",files[i]))
  }
}

save(df, file="all_bounding_boxes.RData")