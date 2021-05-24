import os
import re
from functions.files import filenames
import cv2
import numpy as np
from datetime import datetime

# Parameters
i = 'despeckled'
o = 'deskew'
year = 1858

# Make directories
years = list(range(1858, 1996))
for y in years:
    directory = '/Volumes/T7/probate_files/%s/%d' % (o, y)
    if not os.path.exists(directory):
        os.makedirs(directory)

# Import files
files = filenames(i, year)

for file in files:
    img = cv2.imread(file)

    # convert the image to grayscale and flip the foreground
    # and background to ensure foreground is now "white" and
    # the background is "black"
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    # threshold the image, setting all foreground pixels to
    # 255 and all background pixels to 0
    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )[1]

    # grab the (x, y) coordinates of all pixel values that
    # are greater than zero, then use these coordinates to
    # compute a rotated bounding box that contains all
    # coordinates
    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
    # the `cv2.minAreaRect` function returns values in the
    # range [-90, 0); as the rectangle rotates clockwise the
    # returned angle trends to 0 -- in this special case we
    # need to add 90 degrees to the angle

    if angle % 90 == 0:
        continue
    else:
        if angle > 45:
            angle = -(90 - angle)
        else:
            angle = -angle

        if abs(angle) < 2:
            # rotate the image to deskew it
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )

        else:
            continue

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)

    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
