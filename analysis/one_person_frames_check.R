
summary_by_age_cropped <- d_cropped %>%
  replace_na(list(hand_detected = FALSE, face_detected = FALSE, num_people = 0)) %>%
  # filter(num_people < 2) %>%
  mutate(age_day_bin = cut(age_days, bins, labels=round(bin_starts/30,1))) %>%
  mutate(age_day_bin = as.numeric(as.character(age_day_bin))) %>%
  group_by(age_day_bin,child_id) %>%
  summarize(num_detect = length(face_openpose), num_people = mean(num_people), Face = sum(face_detected) / num_detect,  Hands_Cropped = sum(hand_detected) / num_detect, Hands = sum(hand_openpose) / num_detect)

wide <- summary_by_age_cropped_one_person %>%
  gather(region, prop, Face, Hands_Cropped, Hands)


ggplot(summary_by_age_cropped, 
       aes(x=age_day_bin, y=num_people, 
           size=log10(num_detect))) +
  geom_point(alpha=.2) +
  geom_smooth(span=10, aes(weight = num_detect)) + 
  ylab('Proportion People Detected') + 
  xlab('Age (Months)') +
  ylim(0,.5) +
  theme(legend.position="bottom") +
  facet_grid(.~child_id) + 
  ggthemes::scale_color_solarized(name = "") + 
  scale_size_continuous(name = "Detections (Log 10)") +
  theme(legend.text=element_text(size=8))


ggplot(wide, 
       aes(x=age_day_bin, y=prop, 
           size=log10(num_detect),
           col=region)) +
  geom_point(alpha=.2) +
  geom_smooth(span=10, aes(weight = num_detect)) + 
  # geom_smooth(data = wide_cropped, aes(weight = num_detect),
  # lty = 2, span=10, se = FALSE) +
  ylab('Proportion Detections') + 
  xlab('Age (Months)') +
  ylim(0,.5) +
  theme(legend.position="bottom") +
  facet_grid(.~child_id) + 
  ggthemes::scale_color_solarized(name = "") + 
  scale_size_continuous(name = "Detections (Log 10)") +
  theme(legend.text=element_text(size=8))
