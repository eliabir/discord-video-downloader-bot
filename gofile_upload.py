#!/usr/bin/env python3

from gofile2 import Gofile

def upload_gofile(file_name, vid_path):
    gf = Gofile()

    dl_info = gf.upload(file=f"{vid_path}/{file_name}")

    return dl_info['downloadPage']

if __name__ == '__main__':
    upload_gofile()
