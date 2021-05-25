
import pandas as pd
import sys
import os
import cv2
import numpy as np
import ruptures as rpt
import re
from datetime import datetime


def filenames(input_path, year):
    # Find files
    path = '/Volumes/T7/probate_files/' + input_path + '/' + str(year)
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.png' in file:
                if '._' not in file:
                    files.append(os.path.join(r, file))
    # Tidy files
    files.sort()
    return files


# Parameters
i = 'raw-files'
o = 'cleaned'
year = int(sys.argv[1])

# Make folder if it doesn't exist
directory = '/Volumes/T7/probate_files/%s/%d/' % (o, year)
if not os.path.exists(directory):
    os.makedirs(directory)

# Resizing
# Import results from optimisation
results = pd.read_csv(r'../params/resize/%d.csv' % year)

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

# List of files that have been cleaned
compl = filenames(o, year)
compl = [re.sub(o, i, c) for c in compl]

# List of files that still need to be cleaned
files = filenames(i, year)
files = [f for f in files if f not in compl]

dimen = (2774, 4498)

for file in files:

    # Read in image
    img = cv2.imread(file, 0)
    img = cv2.resize(img, dimen, interpolation = cv2.INTER_AREA)

    """
    REMOVE LARGE BLOBS
    """
    blur = cv2.GaussianBlur(img, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Find contours and draw rectangle
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h >= 200:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)

    """
    TEXT BLOCK
    """
    # Count number of black pixels in each column
    points = np.count_nonzero(img == 0, axis = 0)

    # Kernelised mean change
    model = 'rbf'
    algo = rpt.Pelt(model = model).fit(points)
    result = algo.predict(pen = 10)

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

    # Don't trim too much from right
    if end - start > 2100:
        # Turn all pixels in this range white
        img[:, end:] = 255

    """REMOVE BLOBS"""
    # Create rectangular structuring element and dilate
    white_bg = 255 * np.ones_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
    dilate = cv2.dilate(thresh, kernel, iterations = 10)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        roi = img[y:y + h, x:x + w]
        if h >= 30:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    # Vertical
    white_bg = 255 * np.ones_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 4))
    dilate = cv2.dilate(thresh, kernel, iterations = 11)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        roi = img[y:y + h, x:x + w]
        if w > 80:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    # Find one contour
    median = cv2.medianBlur(img, 21)

    thresh = cv2.threshold(
        median, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dilate = cv2.dilate(thresh, kernel, iterations = 7)

    # Find contours
    cnts, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts = [c for c in cnts if (cv2.boundingRect(c)[0] > 0)]
    cnts = [c for c in cnts if (cv2.boundingRect(c)[1] > 0)]
    cnts = [c for c in cnts if (cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] < img.shape[1])]
    cnts = [c for c in cnts if (cv2.boundingRect(c)[1] + cv2.boundingRect(c)[3] < img.shape[0])]

    # Concatenate all contours
    cnts = np.concatenate(cnts)

    # Determine and draw bounding rectangle
    x, y, w, h = cv2.boundingRect(cnts)
    mask = 255 * np.ones_like(img)
    mask[y:y + h, x:x + w] = img[y:y + h, x:x + w]

    img = mask

    median = cv2.medianBlur(img, 15)
    coords = np.column_stack(np.where(img == 0))
    angle = cv2.minAreaRect(coords)[-1]
    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle

    if angle % 90 != 0:
        if angle > 45:
            angle = -(90 - angle)
        else:
            angle = -angle

        if abs(angle) < 1:
            # rotate the image to deskew it
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img, M, (w, h),
                flags = cv2.INTER_CUBIC,
                borderMode = cv2.BORDER_CONSTANT,
                borderValue = 255
            )
    # Resize
    # New dimensions
    if optimal != 100:
        width = int(img.shape[1] * optimal / 100)
        height = int(img.shape[0] * optimal / 100)
        dim = (width, height)

        # Resize image
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)

    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S") + ' ' + str(round(angle, 2)))
