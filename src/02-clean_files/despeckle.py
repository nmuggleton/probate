# Step 3
import os
import re
from functions.files import filenames
import cv2
import numpy as np
from datetime import datetime

# Parameters
i = 'clipped'
o = 'despeckled'
year = 1858

# Make directories
years = list(range(1858, 1996))
for y in years:
    directory = '/Volumes/T7/probate_files/%s/%d' % (o, y)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Import files
files = filenames(i, year)

files = [file for file in files if int(re.findall(r'\d+', file)[1]) < 1859]

for file in files:
    # Load image, grayscale, Gaussian blur, Otsu's threshold
    img = cv2.imread(file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

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
        if h >= 15:
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
        if ((w > 80) & (h > 60) | (w > 150)):
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    # cv2.imshow('thresh', thresh)
    # cv2.imshow('dilate', dilate)
    # cv2.imshow('image', img)
    # cv2.waitKey()

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)

    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
