"""
Script name: c-remove_border.py
Purpose of script:
Dependencies:
Author: Naomi Muggleton
Date created: 15/03/2021
Date last modified: 08/04/2021
"""

import cv2
import numpy as np

def remove_border(img):
    """
    param:
    - img: image with dodgy border that I want to remove
    """
    mask = np.zeros(img.shape, dtype=np.uint8)
    #
    cnts = cv2.findContours(
        img,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    #
    cv2.fillPoly(mask, cnts, [255,255,255])
    mask = 255 - mask
    res = cv2.bitwise_or(img, mask)
    return res
