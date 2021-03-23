import sys
from import_pngs import *
import os
from png_to_txt import *
from glob import glob

# 1. Get image files from S3 bucket
## Parameters for import
year = sys.argv[1]
prefix = 'raw-files/' + year
local  = '.'
bucket = 'probate-calendar'
client = boto3.client('s3', region_name='us-west-2')
path = '/Users/naomimuggleton/Documents/work/github/probate/03-ocr'

## Import files
os.chdir(path)
import_pngs(prefix, local, bucket, client)

# 2. Convert .png to .txt files
## Make directories for text files
if not os.path.exists('output'):
    os.mkdir('output')

if not os.path.exists('output/' + year):
    os.mkdir('output/' + year)

## Make list of images that are to be converted to text
image_path = glob('raw-files/' + year + '/*')
image_path.sort()

## Convert images to text
convert_text = map(png_to_txt, image_path)
set(convert_text)

# 3. Put text files into S3 bucket
cmd = 'aws s3 mv ./output/ s3://probate-calendar/tesseract/ --recursive --exclude "*.DS_Store*"'
os.system(cmd)