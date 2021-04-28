
# load bounding boxes from openpose detections from the entire dataset
# (created in 2_get_bounding_boxes_per_vid.py using numpy vectors in $GROUP_SCRATCH/Home_Headcam_new/openpose_saycam_flattened)

require(data.table)
require(here)
require(stringr)

INDIR = "/scratch/groups/mcfrank/Home_Headcam_new/bounding_boxes" # CSV files from the npy arrays
OUTDIR = "/scratch/groups/mcfrank/Home_Headcam_new/bounding_boxes_Rds/"

files <- list.files(INDIR) 
# A_20140630_2117_04_bounding_boxes.csv had no detections
print(length(files))

df <- data.frame()

#had to specify columns to get rid of the total column

# file[i] = "A_20130531_0818_03_bounding_boxes_high_conf.csv" 
#  -or-     "A_20130531_0818_03_bounding_boxes.csv"
for (i in 1:length(files)) {
  tmp <- fread(paste(INDIR, files[i], sep='/'), stringsAsFactors = F) 
  if(ncol(tmp)==12) {
    this_vid = str_remove(files[i], "_bounding_boxes.csv")
    tmp$child_id = strsplit(files[i], '_')[[1]][1]
    if(strsplit(files[i], '_bounding_boxes')[[1]][2] == ".csv") {
      file_postfix = "_BBs.Rds"
    } else {
      file_postfix = "_high_conf_BBs.Rds"
    }
    tmp$vid_name = this_vid
    tmp = subset(tmp, mean_confidence!=0)
    #df <- rbindlist(list(df, tmp)) # , use.names = T
    #df = rbind(df, tmp)
    saveRDS(tmp, file=paste0(OUTDIR,this_vid, file_postfix))
  } else {
    print(paste("check file: ",files[i])) # improper number of columns
  }
}

#df <- df %>% mutate(height = ifelse(child_id=="Y", height/480, height),
#                    width = ifelse(child_id=="Y", width/640, width))

#df$area = df$height * df$width
#save(df, file="all_bounding_boxes.RData")

