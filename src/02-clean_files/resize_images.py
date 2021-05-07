
# Step 2
import pandas as pd
import re
import os
import cv2
from datetime import datetime

os.chdir('/Users/naomimuggleton/Documents/work/github/probate/src')

for year in list(range(1858, 1907)):
    results = pd.read_csv(r'params/resize/%d.csv' % year)
    image_path = '/Volumes/T7/probate_files/raw-files/%d/' % year
    output_path = re.sub(image_path, 'raw-files', 'resized')
    results['accuracy'] = results.iloc[:, 1:].sum(axis = 1)

    best = results[results['accuracy'] == results['accuracy'].max()]

    best = best['size'].to_list()
    best.sort()

    if 100 in best:
        optimal = 100
    elif len(best) == 1:
        optimal = best[0]
    elif len(best) % 2 == 1:
        optimal = best[int((len(best) + 1) / 2)]
    else:
        optimal = best[int((len(best)) / 2)]

    if optimal == 100:
        print('Skipping year %d' % year)
    else:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        files = [image_path + image for image in os.listdir(image_path)]
        files.sort()

        for file in files:
            img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
            width = int(img.shape[1] * optimal / 100)
            height = int(img.shape[0] * optimal / 100)
            dim = (width, height)
            resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            dest = re.sub('raw-files', 'resized', file)
            cv2.imwrite(dest, resized)
            print(file + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
