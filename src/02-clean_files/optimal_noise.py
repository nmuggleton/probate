
import pandas as pd
import re
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract

# Set display settings
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 80)

df = pd.read_csv('params/probate_tracker.csv')
df = df[df['year'] < 1895]
filenames = df['filename'].unique().tolist()

filepaths = ['../data/raw-files/' + re.search(r'(\d{4})(?=\.)', file).group(0) + '/' + file for file in filenames]

if not os.path.exists('params/denoise'):
    os.makedirs('params/denoise')

for filepath in filepaths:
    # Remove noise
    img = cv2.imread(filepath, 0)
    _, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)
    sizes = stats[1:, -1] #get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for i in range(0, nlabels - 1):
        if sizes[i] >= 15:   #filter small dotted regions
            img2[labels == i + 1] = 255

    res = cv2.bitwise_not(img2)

    # Correct answers
    answerset = df[df['filename'] == re.search(r'(?<=/\d{4}/).*', filepath).group()]

    answers = answerset['page_header'].unique().tolist() + \
              answerset['name'].unique().tolist() + \
              answerset['date_proved'].unique().tolist() + \
              answerset['effects'].unique().tolist() + \
              answerset['date_of_death'].unique().tolist()

    answers = [re.sub(r'\\n', '\n', answer) for answer in answers if answer == answer]

    # Check accuracy
    txt = pytesseract.image_to_string(res)

    cols = [['filepath'] + answers]
    print(cols)
    out = []
    accuracy = [filepath]

    for answer in answers:
        accuracy = accuracy + [int(answer in txt)]

    out.append(accuracy)
    print(accuracy)

# plt.hist(sizes, bins = list(range(0, 200, 1)))
# plt.show()
