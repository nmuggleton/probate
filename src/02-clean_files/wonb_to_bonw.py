# Step 1 till 1884
from functions.files import filenames
import cv2
from datetime import datetime

# Parameters
i = 'raw-files'
year = 1858

# Import files
files = filenames(i, year)

# Find background colour of each key
for file in files:
    # Read in image
    img = cv2.imread(file, 0)

    # Are more pixels black or white?
    white = len(img[img == 255])
    black = len(img[img == 0])

    # If mostly black, invert image
    if black > white:
        img = cv2.bitwise_not(img)
        cv2.imwrite(file, img)
    print(file + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
