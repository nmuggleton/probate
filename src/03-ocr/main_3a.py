"""
Script name: main_3a.py
Purpose of script: Grab the raw files from the s3 bucket
Dependencies:
    03-ocr/import_pngs.py
Author: Naomi Muggleton (edited by crahal)
Date created: 24/03/2021
Date last modified: 11/04/2021
"""

from import_pngs import import_pngs
import os
import boto3


def load_keys(key_path):
    """Read keys from ./keys/s3_keys"""
    try:
        with open(key_path, 'r') as file:
            keys = file.read().splitlines()
            return keys #note: this a list of key and secret
    except EnvironmentError:
        print('Error loading access token from file')


def main():
    """ main function: i don't think this can be optimized much... """
    key_path = os.path.join(os.getcwd(), '../..', 'keys', 's3_keys')
    aws_key = load_keys(key_path)
    for year in range(1858, 1996):
        client = boto3.client('s3', region_name='us-west-2',
                              aws_access_key_id=aws_key[0],
                              aws_secret_access_key=aws_key[1])
        prefix = 'raw-files/' + str(year)
        bucket = 'probate-calendar'
        data_path = os.path.join(os.getcwd(), '../..', 'data')
        import_pngs(prefix, data_path, bucket, client)


if __name__ == '__main__':
    main()
