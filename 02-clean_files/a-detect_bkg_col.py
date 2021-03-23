import boto3
import cv2
import numpy as np
from io import BytesIO
import pandas as pd

## Parameters
years = list(range(1858, 1996))
dir = 'raw-files/'
bucket_name = 'probate-calendar'
client = boto3.client('s3', region_name='us-west-2')
s3 = boto3.resource('s3', region_name='us-west-2')
bucket = s3.Bucket(bucket_name)

## Get one key per year
prefix = [dir + str(year) for year in years]

keys = []
for i in prefix:
    key = client.list_objects(
        Bucket = bucket_name, MaxKeys = 1, Prefix = i
    )['Contents']
    k = key[0]['Key']
    keys.append(k)

## Find background colour of each key
bkg = []
for i in range(len(keys)):
    ## Read in image
    img = bucket.Object(keys[i]).get().get('Body').read()
    nparray = cv2.imdecode(np.asarray(bytearray(img)), cv2.IMREAD_COLOR)

    ## Split into colour channel
    (channel_b, channel_g, channel_r) = cv2.split(nparray)

    channel_b = channel_b.flatten()
    channel_g = channel_g.flatten()
    channel_r = channel_r.flatten()

    colours_count = {}

    ## Find RBG for each pixel
    for j in range(len(channel_b)):
        RGB = "(" + str(channel_r[j]) + "," + \
            str(channel_g[j]) + "," + str(channel_b[j]) + ")"
        if RGB in colours_count:
            colours_count[RGB] += 1
        else:
            colours_count[RGB] = 1

    ## Are more pixels black or white?
    white = colours_count['(255,255,255)']
    black = colours_count['(0,0,0)']

    if (black > white):
        bkg.append('black')
    else:
        bkg.append('white')

## Save output
df = pd.DataFrame(list(zip(years, bkg)), columns = ['year', 'background'])
df.to_csv(r'background_colour.csv', index = False)
