# Step 2
import os
from functions.files import filenames
import cv2
import numpy as np
import ruptures as rpt
import re
from datetime import datetime

# Parameters
i = 'raw-files'
o = 'clipped'
year = 1871

# Make directories
years = list(range(1858, 1996))
for y in years:
    directory = '/Volumes/T7/probate_files/%s/%d' % (o, y)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Import files
files = filenames(i, year)

# Find left and right margins and convert to white
for file in files:
    # Read in image
    img = cv2.imread(file, 0)

    # Count number of black pixels in each column
    points = np.count_nonzero(img == 0, axis = 0)

    # Kernelised mean change
    model = 'rbf'
    algo = rpt.Pelt(model=model).fit(points)
    result = algo.predict(pen=10)

    # Columns up to first local mean = left border (+50 padding)
    start = result[0] - 50

    # Columns in last local mean = right border (+15 padding)
    end = result[-2] + 50

    # If left margin is less than 100, do nothing
    if start > 100:

        # If average number of black pixels is less than 10
        if np.average(points[:start]) < 10:
            # Turn all pixels in this range white
            img[:, :start] = 255

    # Turn all pixels in this range white
    img[:, end:] = 255

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)
    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
