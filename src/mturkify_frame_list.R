require(tidyverse)
# reshape long to wide to run mturk experiment giving each of 100 subjects 240 frames + 12 gold standard
base_url = "http://langcog.stanford.edu/expts/saycam/frames/"

gold = list.files("data/gold_standard")
set.seed(123)
gold = sample(gold, length(gold), replace=F)
gold_urls = paste(base_url,gold,sep='')

d = read.csv("data/frame_urls2.csv")

w = matrix(d$img_src, nrow=100, byrow=F)

dim(w) # 100 Ss x 240 images (4min @ 1 rating/sec)

gold_inds = 1:12 * 20

wg = cbind(w[,1:20], rep(gold_urls[1], nrow(w))) # 1:20; ni
for(i in 2:length(gold_inds)) {
  start_i = gold_inds[i-1] + 1 # 21, 41, 
  end_i = gold_inds[i]
  wg = cbind(wg, w[,start_i:end_i], rep(gold_urls[i], nrow(w)))
}

dim(wg) # 100 x 252
wg = data.frame(wg)
names(wg) = paste("img_src", 1:ncol(wg), sep='')
write_csv(wg, "data/frame_urls_100x252.csv")

# gold_standard images at column 21, 42, 63, 84, .., 252
# col%%21 == 0
