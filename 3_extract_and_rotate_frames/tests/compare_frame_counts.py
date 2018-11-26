import csv

# master is the longer
# find longer csv and assign appropiately

with open("frames_counted.csv", "rb") as frame_counts:
    master_indices = dict((row[0], row) for row in csv.reader(frame_counts))


with open("../../2_extract_frame_times/data/parsed/checkfile.csv", "rb")\
     as checkfile:
    reader = csv.reader(checkfile)

for row in reader:
    master_row = master_indices.get(row[0])
    if master_row:
        pass
        # print row[0], row[1] == master_row[1]
    else:
        print("*** %s NOT found in frame_counts.csv" % row[0])


# maybe do reverse? or just check counts?
# there is no sense of master list (maybe ffprobe is best, not sure)
