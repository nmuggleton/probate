import os
from os import listdir
from os.path import isfile, join
import cv2
import numpy as np

os.chdir('/Users/naomimuggleton/Desktop')

mypath = '/Users/naomimuggleton/Documents/work/github/probate/probate_records/1858/'

# Despeckle
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
onlyfiles.sort()

for i in range(0, len(onlyfiles) - 1):
    stub = onlyfiles[i]
    file = mypath + stub
    ## Clean
    img = cv2.imread(file, 0)
    _, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)
    sizes = stats[1:, -1] #get CC_STAT_AREA component
    img2 = np.zeros((labels.shape), np.uint8)

    for j in range(0, nlabels - 1):
        if sizes[j] >= 30:   #filter small dotted regions
            img2[labels == j + 1] = 255

    res = cv2.bitwise_not(img2)

    # cv2.imwrite('clean/unclean_' + stub, img)
    # cv2.imwrite('clean/clean_' + stub, res)

    ## Remove dodgy border
    gray = res
    mask = np.zeros(res.shape, dtype=np.uint8)

    cnts = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    cv2.fillPoly(mask, cnts, [255,255,255])
    mask = 255 - mask
    result = cv2.bitwise_or(res, mask)

    cv2.imwrite('clean/' + stub, result)

    print(i)
