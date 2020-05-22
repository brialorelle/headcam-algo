#!/usr/bin/env python3

import os
import argparse
import getpass
import re
import requests

# TODO: use native csvwriter for portability
import pandas as pd

parser = argparse.ArgumentParser(description='Download a volume from databrary.')
parser.add_argument('volume_num', metavar='NUM', type=str, nargs='?', default=564,
                    help='number of the Databrary volume to be downloaded')
parser.add_argument('--output_dir', '-o',
                    help='Directory to save the downloaded volume')
args = parser.parse_args()


def main():
    s = login_databrary()
    download_videos(s, args.volume_num, args.output_dir)


def login_databrary():
    print('Logging into Databrary...')
    URL = "https://nyu.databrary.org//api/user/login"
    PARAMS = {'email': input('Databrary username? '),
              'password': getpass.getpass('Databrary password: ')}
    s = requests.Session()
    r = s.post(url=URL, data=PARAMS)
    print(f'Result of login command (200 = success): {r.status_code}')
    return s


def download_videos(s, volume_info_csv, output_dir, overwrite=False):
    def get_asset_ids_names(s, session_id):
        r = s.get('https://nyu.databrary.org/api/slot/{session_id}/-?assets')
        return [(asset['id'], asset['name']) for asset in r.json()['assets']]

    def url_for_download(session_id, asset_id):
        return f'https://nyu.databrary.org/slot/{session_id}/-/asset/{asset_id}/download'

    print(f'Downloading videos from Databrary into {output_dir}: ')
    vol_info = pd.read_csv(volume_info_csv)
    for i, row in vol_info.iterrows():
        session_id, session_name = row['session-id'], row['session-name']
        print(f'Session {i+1}/len(vol_info): {session_name}')
        for asset_id, asset_name in get_asset_ids_names(s, session_id):
            formatted_filename = re.search(r'(.+)(?:\.AVI)?', asset_name)[1]
            formatted_filepath = os.path.join(output_dir, formatted_filename)
            if not overwrite and os.path.exists(formatted_filepath):
                print('{formatted_filename} already exists, continuing...')
                continue
            print('Downloading {formatted_filename}...')
            r = s.get(url=url_for_download(session_id, asset_id))
            if (r.status_code != 200):
                print(f'Got status code {r.status_code} downloading {formatted_filename}!')
                continue
            # some session names for headcam dataset accidentally have AVI in them
            with open(formatted_filepath, 'wb') as f:
                f.write(r.content)


if __name__ == "__main__":
    main()
