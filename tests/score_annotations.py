import pandas as pd

if __name__ == '__main__':
    for VID_NAME in ['2014-01-01-part2', '061713-1']:
        for suffix in ['face2', 'random2']:
            SAMPLE_CSV_PATH = '/scratch/users/agrawalk/headcam-algo/tests/output/fscore_test/{0}_{1}/{0}_{1}.csv'.format(VID_NAME, suffix)
            df = pd.read_csv(SAMPLE_CSV_PATH)
            sel = df[df['face']]
            rel = df[df['ground_truth'] == 1]
            true_pos = sel[sel['ground_truth'] == 1]
            p = len(true_pos) / float(len(sel))
            r = len(true_pos) / float(len(rel))
            fscore = 2 * p * r / (p + r)

            print('{0}_{1} ({2} frames): '.format(VID_NAME, suffix, len(df)))
            print('selected: {0}, relevant: {1}, sel and rel: {2}'.format(len(sel), len(rel), len(true_pos)))
            print('precision: {0}, recall: {1}, F-score: {2}\n'.format(p, r, fscore))
