#!/usr/bin/env python3

from imgurpython import ImgurClient

def upload_imgur(file_name, file_path, client_id, client_secret):
    client = ImgurClient(client_id, client_secret)

    response = client.upload_from_path(f'{file_path}/{file_name}', config=None, anon=True)

    url = response['link']

    return url

if __name__ == '__main__':
    upload_imgur()

