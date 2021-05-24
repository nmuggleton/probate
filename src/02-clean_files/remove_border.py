# Step 2
import os
from functions.files import filenames
import cv2
import numpy as np
import re
from datetime import datetime

# Parameters
i = 'raw-files'
o = 'border_removed'
year = 1953

# Import files
files = filenames(i, year)

# Make directories
years = list(range(1858, 1996))
for y in years:
    directory = '/Volumes/T7/probate_files/%s/%d' % (o, y)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Find any shadows that are introduced from scanning
for file in files[89323:]:
    # Read in image
    img = cv2.imread(file, 0)

    # Find contours in the image
    cnts = cv2.findContours(
        img,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Remove border
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    mask = np.zeros(img.shape, dtype = np.uint8)
    cv2.fillPoly(mask, cnts, [255, 255, 255])
    mask = 255 - mask
    img = cv2.bitwise_or(img, mask)

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)
    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
