import pandas as pd
import re
import cv2
import pytesseract
import math

# Set display settings
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 80)

df = pd.read_csv('params/probate_tracker.csv')

filenames = df['filename'].unique().tolist()

filepaths = ['../data/raw-files/' + re.search(r'(\d{4})(?=\.)', file).group(0) + '/' + file for file in filenames]

out = []
for i in range(len(filepaths)):
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
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)

    sizes = list(range(1, 101))
    # Rescale
    for size in sizes:
        width = int(img.shape[1] * size / 100)
        height = int(img.shape[0] * size / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        txt = pytesseract.image_to_string(resized)
        correct = 0
        for answer in answers:
            correct += int(answer in txt)

        accuracy = correct / len(answers)

        output = [filenames[i], accuracy, size, correct, len(answers)]
        out.append(output)
        print(output)

results = pd.DataFrame(out, columns = ['filename', 'accuracy', 'size', 'correct', 'length'])

results.to_csv(r'output_1858_1981.csv', index = False)

results = pd.read_csv('output_1858_1981.csv')

# Find optimal size
results['rank'] = results.groupby('filename')['accuracy'].rank('dense', ascending = False)

accuracy = results.loc[results['rank'] == 1]

accuracy['min'] = accuracy.groupby('filename')['size'].transform(min)
accuracy['max'] = accuracy.groupby('filename')['size'].transform(max)
accuracy['count'] = accuracy.groupby('filename')['size'].transform('count')
accuracy['median'] = accuracy.groupby('filename')['size'].transform('median')

a = accuracy[['filename', 'accuracy', 'correct', 'length', 'rank', 'max', 'min', 'median', 'count']].drop_duplicates()

rows = list(range(len(a)))

best = []

for row in rows:

    filename = a.iloc[row].loc[['filename']].item()
    min = a.iloc[row].loc[['min']].item()
    median = a.iloc[row].loc[['median']].item()
    max = a.iloc[row].loc[['max']].item()
    count = a.iloc[row].loc[['count']].item()

    if count == 1:
        best_size = min
    elif max == 100:
        best_size = max
    else:
        best_size = math.floor(median)

    best_row = [filename, best_size]

    best.append(best_row)

# we can remove those set to 100 as no transofmration needed

best = [b for b in best if b[1] < 100]
optimal_size = pd.DataFrame(best, columns = ['file', 'best_size'])

optimal_size['year'] = optimal_size['file'].str.extract(r'_(\d{4})\.')

