# Step 2
import pandas as pd
import re
import os
import cv2
import pytesseract

os.chdir('/Users/naomimuggleton/Documents/work/github/probate/src')

df = pd.read_csv('params/probate_tracker.csv')

filenames = df['filename'].unique().tolist()
path = '/Volumes/T7/probate_files/raw-files/'

filepaths = [path + re.search(r'(\d{4})(?=\.)', file).group(0) + '/' + file for file in filenames]

if not os.path.exists('params/resize'):
    os.makedirs('params/resize')

for i in range(len(filepaths) + 1):
    # Correct answers
    answerset = df[df['filename'] == filenames[i]]

    answers = answerset['page_header'].unique().tolist() + \
        answerset['name'].unique().tolist() + \
        answerset['date_proved'].unique().tolist() + \
        answerset['effects'].unique().tolist() + \
        answerset['date_of_death'].unique().tolist()

    answers = [re.sub(r'\\n', '\n', answer) for answer in answers if answer == answer]

    # Read in file
    filepath = filepaths[i]
    img = cv2.imread(filepath, 0)

    sizes = list(range(1, 101))

    cols = [['size'] + answers]
    print(cols)
    out = []

    # Rescale
    for size in sizes:
        width = int(img.shape[1] * size / 100)
        height = int(img.shape[0] * size / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        txt = pytesseract.image_to_string(resized)

        accuracy = [size]

        for answer in answers:
            accuracy = accuracy + [int(answer in txt)]

        out.append(accuracy)
        print(accuracy)

    out = pd.DataFrame(out, columns = cols)
    dest = 'params/resize/' + str(i + 1858) + '.csv'
    out.to_csv(dest, index = False)
