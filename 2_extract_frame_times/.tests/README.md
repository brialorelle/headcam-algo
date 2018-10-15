this may not be useful right now -- can just test against actual frames outputted by ffmpeg?


Test the output of ffprobe with show_frames. show_frames is more likely to throw an error, so checking this against another method to derive frame count is helpful.

Also, maybe test the last timing of show_frames with actual length of movie? 
