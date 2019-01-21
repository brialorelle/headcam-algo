import os
from xml.dom import minidom

import pandas as pd

if __name__ == '__main__':
    for VID_NAME in ['2014-01-01-part2', '061713-1']:
        for suffix in ['face2', 'random2']:
            CSV_PATH = '/scratch/users/agrawalk/headcam-algo/tests/output/{0}_mtcnn.csv'.format(VID_NAME)
            ANNOT_DIR = '/scratch/users/agrawalk/headcam-algo/tests/output/fscore_test/{0}_{1}/annotations/'.format(VID_NAME, suffix)
            SAMPLE_CSV_PATH = '/scratch/users/agrawalk/headcam-algo/tests/output/fscore_test/{0}_{1}/{0}_{1}.csv'.format(VID_NAME, suffix)

            df = pd.read_csv(CSV_PATH)

            df = df.rename(columns={df.columns[0]: 'name',
                                    df.columns[1]: 'frame',
                                    df.columns[2]: 'face',
                                    df.columns[3]: 'x1',
                                    df.columns[4]: 'y1',
                                    df.columns[5]: 'x2',
                                    df.columns[6]: 'y2'})
            df['ground_truth'] = -1
            df = df.set_index('frame')

            for xml in os.listdir(ANNOT_DIR):
                frame_num = int(xml.split('-')[1][:-4])
                xmldoc = minidom.parse(os.path.join(ANNOT_DIR, xml))
                itemlist = xmldoc.getElementsByTagName('name')
                face_str = itemlist[0].firstChild.nodeValue
                face_present = 1 if face_str == 'face' else 0
                df.at[frame_num, 'ground_truth'] = face_present

            df = df.reset_index()
            df = df[df['ground_truth'] != -1]
            df = df.drop_duplicates(subset='frame')

            print('{0}_{1}: {2}'.format(VID_NAME, suffix, len(df)))

            df.to_csv(SAMPLE_CSV_PATH)
