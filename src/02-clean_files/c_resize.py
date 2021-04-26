"""
Script name: optimal_dpi.py
Purpose of script:
Dependencies: None
Author: Naomi Muggleton
Date created: 08/04/2021
Date last modified: 08/04/2021
"""

import boto3
import pytesseract
import numpy as np
import random
import cv2
import pandas as pd

# Parameters
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

for pref in prefix:
    pages = paginator.paginate(Bucket = bucket_name, Prefix = pref)
    keys = []

    for page in pages:
        for obj in page['Contents']:
            key = obj['Key']
            keys.append(key)

    random_key = random.choice(keys)
    random_keys.append(random_key)

## Select a random page
texts = []

for key in random_keys:
    img = bucket.Object(key).get().get('Body').read()
    np_img = cv2.imdecode(np.asarray(bytearray(img)), cv2.IMREAD_GRAYSCALE)

## Find optimal scale
scales = list(range(100))

config = r'-l eng --oem 1 --psm 6 --dpi 600 -c tessedit_write_images=true'

for scale in scales:
    width = int(np_img.shape[1] * (scale + 1) / 100)
    height = int(np_img.shape[0] * (scale + 1) / 100)
    dim = (width, height)
    resized = cv2.resize(np_img, dim, interpolation = cv2.INTER_AREA)
    txt = pytesseract.image_to_string(resized, config = config)
    texts.append(txt)
    print(scale)

## Does it contain header?
a = ['ADMINISTRATIONS. 1858. 21\n' in text for text in texts] * 1
b = ['BARKER Harold James.' in text for text in texts]
c = ['BARKER John.' in text for text in texts]
d = ['BARKER John Hyde.' in text for text in texts]
e = ['BARKER Lydia.' in text for text in texts]
f = ['Effects under £200.' in text for text in texts]
g = ['Effects under £300.' in text for text in texts]
h = ['Effects under £4,000.' in text for text in texts]
i = ['Effects under £200.' in text for text in texts]
j = ['20 February.' in text for text in texts]
k = ['29 April.' in text for text in texts]
l = ['23 December.' in text for text in texts]
m = ['11 November.' in text for text in texts]
n = ['who died 31 July 1858' in text for text in texts]
o = ['who died 19 October 1857' in text for text in texts]
p = ['who died\n22 May 1855' in text for text in texts]
q = ['who died 13 November 1858' in text for text in texts]
r = ['who died 18 April 1858' in text for text in texts]


df = pd.DataFrame(list(zip(texts, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r)))

df.loc[:, 1:] = df.loc[:, 1:].astype(int)
df['accuracy'] = df.loc[:, 1:].sum(axis = 1)
