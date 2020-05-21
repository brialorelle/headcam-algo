import numpy as np
import time
import datetime
import matplotlib.pyplot as plt


def viz_face_hand_trends(frame_df, condense_by='months'):
    """viz_face_hand_trends: plots the proportion of faces and hands detected by Openpose over time.
    A single point on the graph represents a single day/week/month during which video was recorded. 
    The size of the point represents how many frames of video were recorded for that day/week/month.

    :param frame_df: Frame-level dataframe containing timestamp and openpose outputs for each frame
    in the dataset.
    :param date_birth_child: date of birth of the child being plotted.
    :param condense_by: The time period over which to aggregate video data into a single datapoint.
    Defaults to month, can either be 'days', 'weeks', or 'months'.
    """
    divisor = {'days': 1, 'weeks': 7, 'months': 365.25/12}
    plot_info = [(label, len(df), df['face_openpose'].mean(), df['hand_openpose'].mean())
                 for label, df in frame_df.groupby(frame_df['age_days'] // divisor[condense_by])]
    age, lens, face_prop, hand_prop = zip(*plot_info)

    point_sizes = np.array(lens)
    point_sizes = point_sizes / np.max(point_sizes) * 100
    fig, ax = plt.subplots(figsize=(10,5))

    ax.scatter(age, hand_prop, s=point_sizes, c='C0', label='Hand')
    ax.scatter(age, face_prop, s=point_sizes, c='C1', label='Face')

    ax.legend()
    plt.xlabel(f'Age ({condense_by})')
    plt.ylabel('Prevalence of Hands and Faces')
    plt.show()
