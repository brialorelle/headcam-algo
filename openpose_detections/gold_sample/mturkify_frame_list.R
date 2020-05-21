require(tidyverse)
# reshape long to wide to run mturk experiment giving each of 100 subjects 240 frames + 12 gold standard
base_url = "http://langcog.stanford.edu/expts/saycam/frames/"

gold = list.files("data/gold_standard")
set.seed(123)
gold = sample(gold, length(gold), replace=F)
gold_urls = paste(base_url,gold,sep='')
gold_urls = gold_urls[c(1,2,4,5,9)]

d = read.csv("data/frame_urls.csv")

# 50 images per user = 480 turkers

w = matrix(d$img_src, nrow=480, byrow=F)

dim(w) # 480 Ss x 50 images (4min @ 1 rating/sec)

gold_inds = 1:5 * 10

wg = cbind(w[,1:10], rep(gold_urls[1], nrow(w))) # 1:20; ni
for(i in 2:length(gold_inds)) {
  start_i = gold_inds[i-1] + 1 # 11, 21, 
  end_i = gold_inds[i]
  wg = cbind(wg, w[,start_i:end_i], rep(gold_urls[i], nrow(w)))
}

dim(wg) # 480 x 55
wg = data.frame(wg)
names(wg) = paste("img_src", 1:ncol(wg), sep='')
write_csv(wg, "data/frame_urls_480x55.csv")

# gold_standard images at column 21, 42, 63, 84, .., 252
# col%%21 == 0
