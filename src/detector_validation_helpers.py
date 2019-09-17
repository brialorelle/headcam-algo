import os
import cv2
import numpy as np

from config import *
from utils import get_img

def sample_dataframe(frame_df, sample_size=GOLD_SET_NUM_FRAMES, equal_from_each_child=True):
    """sample_dataframe: generates a random sample of frames from the entire dataset of videos.

    :param frame_df: frame-level dataframe w/ vid_name, frame, and child id columns
    :param sample_size: number of frames to sample
    :param equal_from_each_child: if True, does a stratified sample by child--
    that is, it samples (sample_size / # children) frames from each child. otherwise, a simple
    random sample is performed.
    """
    if equal_from_each_child:
        children = frame_df.groupby('child_id', group_keys=False)
        sample_df = children.apply(lambda x: x.sample(sample_size // len(children)))
    else:
        sample_df = frame_df.sample(sample_size)

    sample_df = sample_df.reset_index(drop=True)
    sample_df = sample_df.sort_values(by=['vid_name', 'frame']).reset_index(drop=True)

    return sample_df

def save_sample_imgs(sample_df, batch_size=1000):
    """save_sample_imgs: Saves images from frames contained in sample dataframe in batches of
    batch_size as .npy arrays (useful for quickly loading+displaying+annotating images).

    :param sample_df: Sample dataframe containing paths to images
    """
    batch_paths = []
    for df_num, s in enumerate(range(0, len(sample_df), batch_size)):
        cut = sample_df[s:s+batch_size]
        print(f'Loading imgs #{df_num}')
        imgs = cut.apply(get_img, axis=1).values
        print(f'Saving imgs #{df_num}')
        batch_fp = os.path.join(OUTPUT, f'sample_imgs_{df_num}.npy'), imgs
        batch_paths.append(batch_fp)
        np.save(batch_fp, imgs)

    return batch_paths

#NOTE: The following function does not currently work on Sherlock for me, as the OpenCV version cannot do imshow(). To use this on Sherlock in a notebook, modify to use plt.imshow() instead (this will be significantly slower, however.)
#TODO: Make this work on Sherlock
def annotate_frames(img_batch_paths):
    """annotate_frames: Helper function to manually annotate frames for the presence of hand (yes/no) 
    and presence of face (yes/no). A sequence of frames is displayed, and for each frame, user 
    presses 'f' to indicate just a face, 'd' to indicate just a hand, 's' to indicate both a face 
    and a hand, 'j' to indicate neither face nor hand, and ' ' to go back one frame. annotations
    are recorded in numpy arrays, which are saved to the specified output directory.

    :param img_batch_paths: list of paths to .npy arrays containing the image frames.
    """
    face_present = np.full(GOLD_SET_NUM_FRAMES, -1)
    hand_present = np.full(GOLD_SET_NUM_FRAMES, -1)
    if os.path.isfile(os.path.join(OUTPUT, 'face_present.npy')):
        print('Loading previous face presence annotations....')
        face_present = np.load(os.path.join(OUTPUT, 'face_present.npy'))
    if os.path.isfile(os.path.join(OUTPUT, 'hand_present.npy')):
        print('Loading previous hand presence annotations....')
        hand_present = np.load(os.path.join(OUTPUT, 'hand_present.npy'))


    i = 0
    for imgs_batch_path in os.listdir(img_batch_paths):
        imgs = np.load(imgs_batch_path)
        idx = 0
        while idx < len(imgs):
            advance_by = 1
            print(f'Frame {i} of {GOLD_SET_NUM_FRAMES}')
            cv2.imshow('Frame', imgs[idx])

            if face_present[i] == -1 or hand_present == -1:
                key = ord('c')
            else:
                key = cv2.waitKey(0)

            if key == ord('c'):
                pass #already annotated this frame, so continue.
            elif key == ord('f'): #Recorded a face
                face_present[i] = 1
                hand_present[i] = 0
                print('Recorded face')
            if key == ord('d'): #Recorded a hand
                face_present[i] = 0
                hand_present[i] = 1
                print('Recorded hand')
            elif key == ord('s'): #Recorded both face and hand
                face_present[i] = 1
                hand_present[i] = 1
                print('Recorded both')
            elif key == ord('j'): #Recorded neither face nor hand
                face_present[i] = 0
                hand_present[i] = 0
                print('Recorded neither')
            elif key != ord(' '):
                advance_by = 0
                print('Invalid input. Try again.')
            elif idx != 0:
                advance_by = -1
                print('Going back')
            else:
                advance_by = 0
                print('Can\'t go back any further')

            i += advance_by
            idx += advance_by

            np.save(os.path.join(OUTPUT, 'face_present.npy'), face_present)
            np.save(os.path.join(OUTPUT, 'hand_present.npy'), hand_present)
    cv2.destroyAllWindows()
    return face_present, hand_present


def calc_prf(predictions, ground_truth, print_vals=False):
    """calc_prf: calculates the precision, recall, and F1 score for a given set of predictions and
    ground truth.

    :param predictions: List of binary predictions (0/1)
    :param ground_truth: List of binary "ground truth" values (0/1)
    :param print_vals: if True, prints the P/R/F scores
    """
    if len(predictions) != len(ground_truth):
        raise ValueError('Lengths of predictions and ground truth don\'t match!')

    predictions, ground_truth = np.array(predictions), np.array(ground_truth)
    pos = predictions[predictions == 1]
    true = ground_truth[ground_truth == 1]
    true_pos = ground_truth[ground_truth + predictions == 2]

    p = len(true_pos) / max(1, len(pos))
    r = len(true_pos) / max(1, len(true))
    denom = 1 if p + r == 0 else p + r
    f1 = 2 * p * r / denom

    if print_vals:
        print(f'Precision: {p} Recall: {r} F1 Score: {f1}')

    return p, r, f1
