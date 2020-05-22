#!/usr/bin/env python3

import os
import argparse
import getpass
import re
import requests

# TODO: use native csvwriter for portability
import pandas as pd

parser = argparse.ArgumentParser(description='Download a volume from databrary.')

# defaults to volume 564, Sullivan et al. headcam dataset
parser.add_argument('volume_num', metavar='NUM', type=str, nargs='?', default=564,
                    help='number of the Databrary volume to be downloaded')
parser.add_argument('--output_dir', '-o',
                    help='Directory to save the downloaded volume')
args = parser.parse_args()


def main():
    s = login_databrary()
    volume_info_csv = download_volume_info(s, args.volume_num, args.output_dir)
    download_videos(s, volume_info_csv, args.output_dir)


def login_databrary():
    URL = "https://nyu.databrary.org//api/user/login"
    PARAMS = {'email': input('Databrary username? '),
              'password': getpass.getpass('Databrary password: ')}
    print('Logging into Databrary...')
    s = requests.Session()
    r = s.post(url=URL, data=PARAMS)
    print(f'Result of login command (200 = success): {r.status_code}')
    return s

def download_volume_info(s, volume_num, output_dir):
    print(f'Downloading volume {volume_num}\'s info csv...')
    r = s.get(f'https://nyu.databrary.org/volume/{volume_num}/csv')
    volume_info_csv = os.path.join(output_dir, f'volume_{volume_num}_info.csv')
    with open(volume_info_csv, 'wb') as f:
        f.write(r.content)
    return volume_info_csv

def download_videos(s, volume_info_csv, output_dir, overwrite=False):
    def get_asset_ids_names(s, session_id):
        r = s.get(f'https://nyu.databrary.org/api/slot/{session_id}/-?assets')
        return [(asset['id'], asset['name']) for asset in r.json()['assets']]

    def url_for_download(session_id, asset_id):
        return f'https://nyu.databrary.org/slot/{session_id}/-/asset/{asset_id}/download'

    print(f'Downloading videos from Databrary into {output_dir}: ')
    vol_info = pd.read_csv(volume_info_csv)
    for i, row in vol_info.iterrows():
        session_id, session_name = row['session-id'], row['session-name']
        print(f'Session {i+1}/{len(vol_info)}: {session_name}')
        for asset_id, asset_name in get_asset_ids_names(s, session_id):
            # Remove AVI from session names that accidentally have it
            vid_name = re.search(r'(.+)(?:\.AVI)?', asset_name)[1] + '.mp4'
            vid_path = os.path.join(output_dir, vid_name)
            if not overwrite and os.path.exists(vid_path):
                print(f'{vid_name} already exists, continuing...')
                continue
            print(f'Downloading {vid_name}...')
            r = s.get(url=url_for_download(session_id, asset_id))
            if (r.status_code != 200):
                print(f'Got status code {r.status_code} downloading {vid_name}!')
                continue
            with open(vid_path, 'wb') as f:
                f.write(r.content)
                del r  # Free memory


if __name__ == "__main__":
    main()
