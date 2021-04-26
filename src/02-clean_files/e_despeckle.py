"""
Script name: d-despeckle.py
Purpose of script:
Dependencies:
Author: Naomi Muggleton
Date created: 15/03/2021
Date last modified: 08/04/2021
"""

import cv2
import numpy as np

def despeckle(img):
    """
    param:
    - img: speckly image that we want to clean
    """
    _, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)

    sizes = stats[1:, -1] #get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for j in range(0, nlabels - 1):
        if sizes[j] >= 30:   #filter small dotted regions
            img2[labels == j + 1] = 255

    res = cv2.bitwise_not(img2)
    return res
