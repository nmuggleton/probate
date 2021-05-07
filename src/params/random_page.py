
import boto3
from pathlib import Path
import random
import re

## Parameters
bucket_name = 'probate-calendar'
region = 'us-west-2'
dir = 'raw-files/'
random.seed(10)

## Set up AWS SDK
s3 = boto3.resource('s3', region_name = region)
bucket = s3.Bucket(bucket_name)

client = boto3.client('s3', region_name = region)
paginator = client.get_paginator('list_objects_v2')

## Get keys
prefix = [dir + str(year) for year in list(range(1858, 1996))]
random_keys = []

## Download files
Path('random_img').mkdir(exist_ok=True)

for pref in prefix:
    pages = paginator.paginate(Bucket = bucket_name, Prefix = pref)
    keys = []

    for page in pages:
        for obj in page['Contents']:
            key = obj['Key']
            keys.append(key)

    random_key = random.choice(keys)
    future_name = re.sub(r'raw-files/\d+', 'random_img', random_key)
    client.download_file(bucket_name, random_key, future_name)
    print(random_key)
