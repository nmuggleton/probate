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
