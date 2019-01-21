import pandas as pd
import os
import shutil

if __name__ == '__main__':
    for VID_NAME in ['2014-01-01-part2', '061713-1']:
        for suffix in ['face', 'random']:
            SAMPLE_DIR = '/scratch/users/agrawalk/headcam-algo/tests/output/fscore_test/{0}_{1}/'.format(VID_NAME, suffix)
            df = pd.read_csv(os.path.join(SAMPLE_DIR, '{0}_{1}.csv'.format(VID_NAME, suffix)))
            sel = df[df['face'] == True]
            non_sel = df[df['face'] == False]

            groups = {}
            groups['true_pos'] = sel[sel['ground_truth'] == 1]
            groups['false_pos'] = sel[sel['ground_truth'] == 0]

            groups['true_neg'] = non_sel[non_sel['ground_truth'] == 0]
            groups['false_neg'] = non_sel[non_sel['ground_truth'] == 1]

            for group in groups:
                GROUP_DIR = os.path.join(SAMPLE_DIR, group)
                if not os.path.exists(GROUP_DIR):
                    os.mkdir(GROUP_DIR)
                for frame in groups[group]['frame']:
                    frame = str(frame)
                    frame = '0' * (5 - len(frame)) + frame
                    shutil.move(os.path.join(SAMPLE_DIR, 'image-{0}.jpg'.format(frame)), GROUP_DIR)
