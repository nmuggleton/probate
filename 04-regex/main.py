import sys
from import_txts import *
import os
from glob import glob

# 1. Get image files from S3 bucket
## Parameters for import
year = sys.argv[1]
prefix = 'tesseract/' + year
local  = '.'
bucket = 'probate-calendar'
client = boto3.client('s3', region_name='us-west-2')
path = '/Users/naomimuggleton/Documents/work/github/probate/04-regex'
next_token = ''

## Import files
os.chdir(path)
import_txts(prefix, local, bucket, client)

# 2. Convert .png to .txt files
## Make list of images that are to be converted to text
image_path = glob('tesseract/' + year + '/*')
image_path.sort()

## Convert images to text
convert_text = map(png_to_txt, image_path)
set(convert_text)
