import pandas as pd
import re
import cv2
import pytesseract

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

