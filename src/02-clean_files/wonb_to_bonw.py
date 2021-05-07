# Step 1
import cv2
import os
import re

# Parameters
path = '/Volumes/T7/probate_files/raw-files'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.png' in file:
            files.append(os.path.join(r, file))

files.sort()

files = [file for file in files if int(re.findall(r'\d+', file)[1]) > 1902]

files = [file for file in files if not ('/._' in file)]

# Find background colour of each key
bkg = []
for file in files:
    # Read in image
    img = cv2.imread(file, 0)
    # Are more pixels black or white?
    white = len(img[img == 255])
    black = len(img[img == 0])
    # If mostly black, invert image
    if black > white:
        cv2.imwrite(file, cv2.bitwise_not(img))
    print(file + ' complete.')
