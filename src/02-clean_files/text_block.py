import os
import cv2
import numpy as np
import ruptures as rpt
import re

# Parameters
path = '/Volumes/T7/probate_files/resized/1858'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.png' in file:
            files.append(os.path.join(r, file))

files.sort()

files = [file for file in files if not ('/._' in file)]

for file in files:

    img = cv2.imread(file, 0)
    points = np.count_nonzero(img == 0, axis = 0)
    model='rbf'
    algo = rpt.Pelt(model=model).fit(points)
    result = algo.predict(pen=10)
    start = result[0] - 50
    end = result[-2] + 50

    if start > 100:
        if np.average(points[:start]) < 10:
            img[:,:start] = 255

    img[:,end:] = 255
    location = re.sub('resized', 'clipped', file)
    cv2.imwrite(location, img)
    print(location)

