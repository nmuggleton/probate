import os
import re


def filenames(input_path, year):
    # Find files
    path = '/Volumes/T7/probate_files/' + input_path
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.png' in file:
                files.append(os.path.join(r, file))

    # Tidy files
    files.sort()
    files = [file for file in files if int(re.findall(r'\d+', file)[1]) >= year]
    files = [file for file in files if not ('/._' in file)]
    return files
