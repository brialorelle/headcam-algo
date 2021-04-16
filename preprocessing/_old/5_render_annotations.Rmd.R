
# Render out images based on annotations if desired
## True positives on faces?
```{r eval=FALSE}
faces_only_op_cor <- m %>%
  filter(faces == TRUE) %>%
  filter(face_openpose == TRUE)

# how about images where open pose got it? these should be most obvious
dir.create(paste0('faces_tp/'))
for (i in seq(1,length(faces_only_op_cor$full_image_path),1)){
  image_read(as.character(faces_only_op_cor$full_image_path[i])) %>%
    image_append(stack = FALSE) %>%
    image_write(file.path(paste0("faces_tp/", faces_only_op_cor$short_image_path[i])))
}
```

## False positives on facs?
```{r eval=FALSE}
to_write <- m %>%
  filter(faces == FALSE) %>%
  filter(face_openpose == TRUE)

# how about images where open pose got it? these should be most obvious
dir.create(paste0('faces_fp/'))
for (i in seq(1,length(to_write$full_image_path),1)){
  image_read(as.character(to_write$full_image_path[i])) %>%
    image_append(stack = FALSE) %>%
    image_write(file.path(paste0("faces_fp/", to_write$short_image_path[i])))
}

```

## False negatives on faces?
```{r eval=FALSE}
to_write <- m %>%
  filter(faces == TRUE) %>%
  filter(face_openpose == FALSE)

# how about images where open pose got it? these should be most obvious
dir.create(paste0('faces_fn/'))
for (i in seq(1,length(to_write$full_image_path),1)){
  image_read(as.character(to_write$full_image_path[i])) %>%
    image_append(stack = FALSE) %>%
    image_write(file.path(paste0("faces_fn/", to_write$short_image_path[i])))
}

```
