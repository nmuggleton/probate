"""
Script name: 02-clean_files/main.py
Purpose of script: To take raw files and improve image quality by cleaning
Dependencies: None
Author: Naomi Muggleton
Date created: 24/03/2021
Date last modified: 28/05/2021
"""

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
    path = os.path.join('/Volumes/T7/probate_files', input_path, str(year))
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

if year in list(range(1858, 1872)):
    kernel_size = 15
    blur_size = 7
else:
    kernel_size = 10
    blur_size = 17

# Make folder if it doesn't exist
output_path = os.path.join('/Volumes/T7/probate_files', o, str(year))
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Resizing
# Import results from optimisation
results = pd.read_csv(r'../params/resize/%d.csv' % year)

# Determine paths
image_path = os.path.join('/Volumes/T7/probate_files', i, str(year))

# Find the best resolution for image
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

# Dimension that's expected for all files
dimen = (2774, 4498)

for file in files:
    # Read in image
    img = cv2.imread(file, 0)

    """
    1. IMAGE SIZE
       Ensure that the image dimensions match expected shape so that pixel assumptions are met
    """
    img = cv2.resize(img, dimen, interpolation = cv2.INTER_AREA)

    """
    2. BLACK-ON-WHITE
       Tesseract performs poorly with white-on-black text so invert if needed
    """
    # Are more pixels black or white?
    white = len(img[img == 255])
    black = len(img[img == 0])

    # If mostly black, invert image
    if black > white:
        img = cv2.bitwise_not(img)

    """
    3. REMOVE LARGE BLOBS
       a) Blobs bigger than 200 pixels can't be a letter and must be noise so remove
    """
    # Blur image and ensure all pixels are pure black or white
    blur = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Find contours and draw mask
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    mask = np.zeros(img.shape, dtype = np.uint8)

    # For each contour measure size and convert to white if larger than 200 pixels
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h >= 200:
            cv2.fillPoly(mask, c, [255, 255, 255])

    """
       b) Blobs that are still visible after closing morphology with extreme value (51) can't be a letter so remove
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51))
    res = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations = 3)
    res = cv2.bitwise_not(res)
    img[res == 0] = 255

    """
       c) Finally, search for any outstanding large blobs of black pixels with size of 200+ pixels
    """
    # Blur image and ensure all pixels are pure black or white
    blur = cv2.GaussianBlur(img, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Find contours and draw rectangle
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # For each contour measure size and convert to white if larger than 200 pixels
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h >= 200:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)

    """
    4. FIND PAGE MARGINS
       We can run a model that finds deviations in the number of black pixels per column of pixels in array. Mean change
       indicates a switch from margin-to-non-margin and vice versa
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
        # if np.average(points[:start]) < 10:
        # Turn all pixels in this range white
        img[:, :start] = 255

    # Don't trim too much from right
    if end - start > 2100:
        # Turn all pixels in this range white
        img[:, end:] = 255

    """
    5. BOUNDING BOXES
       a) Bounding box per line of text: identify vertical lines of text by dilating pixels horizontally. If text, the 
       height will be greater than  30 pixels once stretched. Otherwise, pixels represent noise and should be removed.
    """
    # Create rectangular structuring element and dilate
    white_bg = 255 * np.ones_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, 1))
    dilate = cv2.dilate(thresh, kernel, iterations = 10)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # If height of bounding box is greater than 30 then keep
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        roi = img[y:y + h, x:x + w]
        if h >= 30:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    """
       b) Bounding box per paragraph: identify vertical lines of text by dilating pixels horizontally and veertically 
       (rectangle). If text, the width will be greater than 80 pixels.
    """
    # Vertical
    white_bg = 255 * np.ones_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 4))
    dilate = cv2.dilate(thresh, kernel, iterations = 11)

    # Find contours and draw rectangle
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # If width of bounding box is greater than 80 then keep
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        roi = img[y:y + h, x:x + w]
        if w > 80:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    """
       c) Bounding box per page: identify thelimits to each page and remove points outside of this sapce. 
    """
    # Find one contour
    median = cv2.medianBlur(img, 21)
    thresh = cv2.threshold(
        median, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Dilate image
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

    """
     6. REMOVE SMALL SPECKLES
        Remove all contours that are too small to be a letter or part of a letter (e.g., dot above the letter i)
    """
    # Ensure that image is black and white
    _, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    # Find connected components and sizes
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)
    sizes = stats[1:, -1]

    # Create blank image
    img2 = np.zeros((labels.shape), np.uint8)

    # If size is less than 30 pixels then noise; don't copy to img2
    for j in range(0, nlabels - 1):
        if sizes[j] < 30:
            img2[labels == j + 1] = 0

    # Invert image
    img2 = cv2.bitwise_not(img2)

    """
    7. DESKEW IMAGE
       Ensure that the margins are parallel to the page border
    """
    # Blur image
    median = cv2.medianBlur(img, 15)
    coords = np.column_stack(np.where(img == 0))
    angle = cv2.minAreaRect(coords)[-1]

    # If angle is flush (e.g., 90) then do nothing
    if angle % 90 != 0:
        # If angle is greater than 45 then find the acute angle
        if angle > 45:
            angle = -(90 - angle)
        # Otherwise invert angle
        else:
            angle = -angle

        # If angle is large then do nothing (potential miscalculation)
        if abs(angle) < 1:
            # Rotate the image to de-skew it
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img, M, (w, h),
                flags = cv2.INTER_CUBIC,
                borderMode = cv2.BORDER_CONSTANT,
                borderValue = 255
            )

    """
    8. RESIZE IMAGE
       Some images should be resied to optimise the accuracy of Tesseract. Params learned from random sampling of pages
       and accuracy detection.
    """
    # If already optimal do nothing
    if optimal != 100:
        # Else reshape accurding to optimal size
        width = int(img.shape[1] * optimal / 100)
        height = int(img.shape[0] * optimal / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)

    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S") + ' ' + str(round(angle, 2)))
