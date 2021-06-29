"""
Script name: 02-clean_files/main.py
Purpose of script: To take raw files and improve image quality by cleaning
Dependencies: None
Author: Naomi Muggleton
Date created: 24/03/2021
Date last modified: 28/05/2021
"""

import pandas as pd
import sys
from cleaner import *
import multiprocessing
from joblib import Parallel, delayed
import re

os.environ['OMP_THREAD_LIMIT'] = '1'  # avoid conflicts in thread scheduling

# Parameters
i = 'raw-files'
o = 'cleaned'
y = sys.argv[1]


def make_per_year(year, input_path, output_path):
    """
    :param year:
    :param input_path:
    :param output_path:
    :return:
    """

    """
    1. Make folder if it doesn't exist
    """
    output = os.path.join('/Volumes/T7/probate_files', output_path, str(year))
    if not os.path.exists(output):
        os.makedirs(output)

    """
    2. Files that need to be cleaned
    """
    # List of files that have been cleaned
    complete = filenames(output_path, year)
    complete = [re.sub(output_path, input_path, c) for c in complete]

    # List of files that still need to be cleaned
    files = filenames(input_path, year)
    files = [f for f in files if f not in complete]

    """
    3. Cleaner params
        a) Kernel and blur sizes
    """
    if year in list(range(1858, 1872)):
        kernel_size = 15
        blur_size = 7

    elif year in list(range(1872, 1892)):
        kernel_size = 10
        blur_size = 17
    else:
        kernel_size = 15
        blur_size = 7

    if year in list(range(1858, 1892)):
        padding_size = 50
    else:
        padding_size = 15

    """
        b) Optimal size (determined by parameter tuning) 
    """
    # Import best image resolution
    results = pd.read_csv(r'../params/resize/%d.csv' % year)
    results['accuracy'] = results.iloc[:, 1:].sum(axis=1)
    best = results[results['accuracy'] == results['accuracy'].max()]
    best = best['size'].to_list()
    best.sort()

    # If original size was one of best, keep as best
    if 100 in best:
        optimal = 100

    # If only one value was best, choose best
    elif len(best) == 1:
        optimal = best[0]

    # If many were best, choose median (odd)
    elif len(best) % 2 == 1:
        optimal = best[int((len(best) + 1) / 2)]

    # If many were best, choose median (even)
    else:
        optimal = best[int((len(best)) / 2)]

    for file in files:
        clean_file(file, blur_size, padding_size, year, kernel_size, optimal, input_path, output_path)


def main(start_year, end_year):
    data_path = '/Volumes/T7/probate_files'
    out_path = os.path.join(data_path, output_path)

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    num_cores = multiprocessing.cpu_count()

    inputs = range(start_year, end_year)
    Parallel(n_jobs=num_cores)(delayed(make_per_year)(inp, input_path, output_path) for inp in inputs)


if __name__ == '__main__':
    start_year = int(sys.argv[1].split('=')[1])
    end_year = int(sys.argv[2].split('=')[1])
    output_path = o
    input_path = i
    main(start_year, end_year)
