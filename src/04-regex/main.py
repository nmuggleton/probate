"""
Script name: 04-regex/main.py
Purpose of script: Extract data from .txt files
Dependencies: 03-ocr/main.py
Author: Naomi Muggleton
Date created: 19/04/2021
Date last modified: 21/06/2021
"""

import os
import nltk
import re
import pandas as pd
from fuzzywuzzy import process


def filenames(input_path, y):
    # Find file names
    path = os.path.join('/Volumes/T7/probate_files', input_path, str(y))
    file_names = []
    for r, d, f in os.walk(path):
        for file_name in f:
            if '.txt' in file_name:
                if '._' not in file_name:
                    file_names.append(os.path.join(r, file_name))
    # Tidy files
    file_names.sort()
    return file_names


# Split into people
def par_tokenize(text):
    paragraphs = re.compile(r'(?ms)\s(?=[A-Z]+\s\w+)').split(text)
    paragraphs = [p for p in paragraphs if len(nltk.sent_tokenize(p)) >= 4]
    return paragraphs


# Set parameters
year = 1861
i = 'text'

# List files
files = filenames(i, year)

data = []

for file in files:

    """
    SPLIT BY PAGE
    """

    # Import page
    page = open(file, 'r').read()

    # Differentiate between word boundaries and cross-line hyphenation
    page = page.replace('-\n', '')
    page = page.replace('\\', '')

    """
    SPLIT BY INDIVIDUAL
    """
    # Each item in list represents an individual
    people = par_tokenize(page)

    for person in people:
        sentence_list = nltk.sent_tokenize(person)
        sentence_dict = {idx: el for idx, el in enumerate(sentence_list)}

        """
        NAME OF DECEASED
        """
        if re.match(r'^[A-Z]+\s\w', sentence_list[0]):
            name = sentence_list[0]
        else:
            name = ''

        """
        DATE PROVED
        """
        if re.match(r'^\d{1,2}\s[A-Z][a-z]+', sentence_list[1]):
            date = re.findall(r'\d{1,2}\s[A-Z][a-z]+', sentence_list[1])[0]
        elif re.match(r'\d{1,2}\s[A-Z][a-z]+', sentence_list[0]):
            date = re.findall(r'\d{1,2}\s[A-Z][a-z]+', sentence_list[0])[0]
        else:
            date = ''
        """
        EFFECTS
        """
        matches = process.extract("Effects under £", sentence_dict, limit = 1)
        match_index = matches[0][2]
        effects_sentence = sentence_list[match_index]
        try:
            effects = re.findall(r'\w+\s\w+\s£\d.*', effects_sentence)[0]
        except IndexError:
            effects = ''

        """
        BIO
        """
        bio = ' '.join(sentence_list[2:])
        bio = re.sub('\n', ' ', bio)
        bio = re.sub(effects, '', bio)
        bio = re.sub(r'\s\s', ' ', bio)

        output = {'name': name, 'effects': effects, 'date': date, 'bio': bio}

        data.append(output)
        print(name)

df = pd.DataFrame(data)

df.to_csv(
    '/Volumes/T7/probate_files/regex_output/%d.csv' % year,
    index = False
)

