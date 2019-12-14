require("RCurl")

frame_urls = read.csv("~/Documents/GitHub/headcam-algo/src/data/frame_urls2.csv")

urls = as.character(frame_urls$img_src)

startTime = Sys.time()
exists = lapply(urls, url.exists)
stopTime = Sys.time()
# how long to check all of them? (maybe related to slow load time?)
stopTime - startTime

missing_inds = which(exists==F)