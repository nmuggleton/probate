# Step 3
import os
import pandas as pd
import re
import cv2
from datetime import datetime

# Parameters
os.chdir('/Users/naomimuggleton/Documents/work/github/probate/src')
i = 'raw-files'
o = 'resized'

# Determine whether image needs to be resized
for year in list(range(1894, 1908)):
    # Import results from optimisation
    results = pd.read_csv(r'params/resize/%d.csv' % year)

    # Determine paths
    image_path = '/Volumes/T7/probate_files/%s/%d/' % (i, year)
    output_path = re.sub(image_path, i, o)

    # Find the best
    results['accuracy'] = results.iloc[:, 1:].sum(axis = 1)
    best = results[results['accuracy'] == results['accuracy'].max()]
    best = best['size'].to_list()
    best.sort()

    # If original size was one of best, keep as best
    if 100 in best:
        optimal = 100

    # If only one value was best, choose best
    elif len(best) == 1:
        optimal = best[0]

    # If many were best, choose median (odd)
    elif len(best) % 2 == 1:
        optimal = best[int((len(best) + 1) / 2)]

    # If many were best, choose median (even)
    else:
        optimal = best[int((len(best)) / 2)]

    # If original was best, do nothing
    if optimal == 100:
        print('Skipping year %d' % year)

    # Else resize
    else:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = [image_path + image for image in os.listdir(image_path)]
        files.sort()
        files = [file for file in files if not ('/._' in file)]

        for file in files:
            # Read in image
            img = cv2.imread(file, 0)

            # New dimensions
            width = int(img.shape[1] * optimal / 100)
            height = int(img.shape[0] * optimal / 100)
            dim = (width, height)

            # Resize image
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

            # Save file
            dest = re.sub(i, o, file)
            cv2.imwrite(dest, img)
            print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
