import pandas as pd
import boto3
import cv2
import numpy as np
from pathlib import Path

## Parameters
bucket_name = 'probate-calendar'
region = 'us-west-2'
dir = 'raw-files/'

## Find years that need to be inverted
bkg = pd.read_csv('background_colour.csv')
black = bkg[bkg['background'] == 'black']
years = list(black['year'])

## Set up AWS SDK
s3 = boto3.resource('s3', region_name = region)
bucket = s3.Bucket(bucket_name)

client = boto3.client('s3', region_name = region)
paginator = client.get_paginator('list_objects_v2')

## Get keys
prefix = [dir + str(year) for year in years]
keys = []

for pref in prefix:
    pages = paginator.paginate(Bucket = bucket_name, Prefix = pref)
    for page in pages:
        for obj in page['Contents']:
            key = obj['Key']
            keys.append(key)

## Create directories for inverted files
Path("inverted").mkdir(parents=True, exist_ok=True)
for year in years:
    Path("inverted/" + str(year)).mkdir(parents=True, exist_ok=True)

keys2 = keys[166316:]
for key in keys2:
    img = bucket.Object(key).get().get('Body').read()
    nparray = cv2.imdecode(np.asarray(bytearray(img)), cv2.IMREAD_COLOR)
    invert = cv2.bitwise_not(nparray)
    file_name = key.replace('raw-files', 'inverted')
    cv2.imwrite(file_name, invert)
    print(file_name + ' complete.')
