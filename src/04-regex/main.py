"""
Script name:
Purpose of script:
Dependencies:
Author: Naomi Muggleton
Date created: 19/04/2021
Date last modified: 19/04/2021
"""

# Import modules
import os
import regex as re
import pandas as pd
from fuzzywuzzy import fuzz

# Set parameters
year = 1858
i = 'text'

# Set display settings
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 80)

# List files
filepath = os.path.join('/', 'Volumes', 'T7', 'probate_files', i, str(year))
files = os.listdir(filepath)
files.sort()
files = ['/'.join([filepath, file]) for file in files]

# Import text
df = pd.DataFrame(columns = ['file', 'page', 'person'])

tried = []
for file in files:
    try:
        page = open(file, 'r').read()
        page = re.sub(r'\. \.', '.', page)
        page = re.sub(r'\n\s+', '\n', page)
        page = re.sub(r'\s+\n', '\n', page)
        page = re.sub(r'\s+-', '', page)
        page = re.sub(r'\.\s+\.', '.', page)
        page = re.split(r'(?<=\d{4}.*)\n', page, maxsplit = 1)
        meta = page[0]
        people = re.split(r'\n(?=[A-Z]+\s+[A-Z][a-z]+)', page[1])
        page_output = list(zip([file] * len(people), [meta] * len(people), people))
        page_df = pd.DataFrame(page_output, columns = ['file', 'page', 'person'])
        df = df.append(page_df, ignore_index = True)
        print(file)
    except IndexError:
        tried.append(file)


# Drop pages that are in irregular format
keywords = [
    'IRISH', 'PROBATES', 'SEALED', 'SCOTCH', 'CONFIRMATIONS', 'PROVED', 'PREROGATIVE', 'COURT', 'CANTERBURY', 'GRANTED'
]

keyword_string = '|'.join(keywords)
df = df[~df['page'].str.contains(keyword_string)]

# Identify whether the page contains wills or administrations
row_count = df.shape[0]
df['type'] = ''

for row in list(range(row_count)):
    string = df.loc[:, 'page'].iloc[row]
    wills = fuzz.partial_ratio(string, 'WILLS')
    if wills >= 70:
        probate_type = 'wills'
    else:
        administrations = fuzz.partial_ratio(string, 'ADMINISTRATIONS')
        if administrations >= 70:
            probate_type = 'administrations'
        else:
            probate_type = ''
    df.loc[:, 'type'].iloc[row] = probate_type
    print(row)

df['year'] = df['page'].str.extract(r'(\b\d{4}\b)', expand = True)
df['page_no'] = df['page'].str.extract(r'(\b\d{1,3}\b)', expand = True)
df['name'] = df['person'].str.extract(r'(^[A-Z]+(\s[A-Z][a-z]+)+)\.', expand = True)[0]
df['proved'] = df['person'].str.extract(r'(\d+\s\w+)')
df['effects'] = df['person'].str.extract(r'\n.*(£\d+(,\d+)?)', expand = True)

df['leftover'] = df['person'].str.split(r'\.', expand = True)
df['name_str'] = df['person'].str.split(r'\.', expand = True)[0]
df['proved_str'] = df['person'].str.split(r'\.', expand = True)[1]
df['will_str'] = df['person'].str.split(r'\.', expand = True, n = 2)[2]
df['person_str'] = df['person'].str.split(r'(?= (The Will|Letters))', expand = True, n = 2)[2]
df['person_str'] = df['person_str'].str.replace(r'\n', ' ')
df['person_str'] = df['person_str'].str.replace(r'[A-Za-z]+ [A-Za-z]+ £\d+(\. )?', '')
df['person_str'] = df['person_str'].str.replace(r'\s+', ' ')
df['person'].str.rsplit('died', expand = True, n = 1)


df.dropna(subset = ['name'])
df.dropna(subset = ['proved'])
df.dropna(subset = ['effects'])
