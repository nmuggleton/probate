"""
Script name: png_to_txt.py
Purpose of script: Function to apply tesseract to images and export text
Dependencies: None
Author: Naomi Muggleton
Date created: 24/03/2021
Date last modified: 08/04/2021
"""

import cv2
import pytesseract
import re

def png_to_txt(image_path):
    """
    param:
    - image_path: path to the image that I want read
    """
    img = cv2.imread(image_path, 0)

    ## OCR
    txt = pytesseract.image_to_string(img, config = r'--psm 1 --oem 1')
    print(txt)

    text_path = re.sub('.png', '.txt', image_path, flags = re.I)
    text_path = re.sub('raw-files', 'output', text_path, flags = re.I)

    f = open(text_path, 'w')
    f.write(txt)
    f.close()
    print(text_path + ' complete.')
