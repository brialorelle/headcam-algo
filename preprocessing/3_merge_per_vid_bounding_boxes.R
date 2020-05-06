
# load bounding boxes from openpose detections from the entire dataset
# (created in get_bounding_boxes_per_vid.py using numpy vectors in $GROUP_SCRATCH/openpose_flattened_whole)

require(data.table)
require(here)
require(stringr)

files <- list.files(here("bounding_boxes")) # 1927 vids
# A_20140630_2117_04_bounding_boxes.csv had no detections

load(here("src/data/vid_info.RData")) # vid_info
downup = fread(here("src/data/video_right-side-up.csv"), stringsAsFactors = F)

df <- data.frame()

Yb <- as.Date("20180214", "%Y%m%d")

#had to specify columns to get rid of the total column
for (i in 1:length(files)) {
  tmp <- fread(paste(here("bounding_boxes"), files[i], sep='/'), stringsAsFactors = F) 
  if(ncol(tmp)==9) {
    tmp$V1 = NULL
    this_vid = str_remove(files[i], "_bounding_boxes.csv")
    tmp$child_id = strsplit(files[i], '_')[[1]][1]
    tmp$vid_name = this_vid
    tmp$age_days = vid_info[which(vid_info$vid_name == this_vid)[1],]$age_days
    if(is.na(tmp$age_days) & tmp$child_id=="Y") {
      cur_age = as.Date(strsplit(files[i], '_')[[1]][2], "%Y%m%d")
      tmp$age_days = as.numeric(cur_age - Yb)
    }
    tmp$right_side_up = downup[which(downup$video == this_vid),]$right_side_up
    # remove any rows with all 0 bounding box + confidences (~50%)
    tmp = subset(tmp, mean_confidence!=0)
    #df <- rbindlist(list(df, tmp)) # , use.names = T
    df = rbind(df, tmp)
  } else {
    print(paste("check file: ",files[i]))
  }
}

df <- df %>% mutate(height = ifelse(child_id=="Y", height/480, height),
                    width = ifelse(child_id=="Y", width/640, width))

df$area = df$height * df$width
save(df, file="data/all_bounding_boxes.RData")

