"""
Script name: 03-ocr/main.py
Purpose of script: To take clean files, run tesseract, and store output
Dependencies:
    03-ocr/png_to_txt.py
Author: Naomi Muggleton (edited by crahal)
Date created: 24/03/2021
Date last modified: 28/05/2021
"""


import os
import sys
from png_to_txt import png_to_txt, PyTessy
import multiprocessing
from joblib import Parallel, delayed
import itertools
import re

os.environ['OMP_THREAD_LIMIT'] = '1'  # avoid conflicts in thread scheduling


def make_per_year(year, psm, white_list):
    """
    Makes output files on a per year basis
    Note: this is the 'outer' parralized loop
    :param year:
    :return: None
    """
    # call PyTessy once per job only, pass it to png_to_txt
    ocr_reader = PyTessy()
    # set paths again, easier hack than input args
    data_path = '/Volumes/T7/probate_files'
    raw_path = os.path.join(data_path, 'cleaned')
    out_path = os.path.join(data_path, 'text')

    if not os.path.exists(os.path.join(out_path, str(year))):
        os.mkdir(os.path.join(out_path, str(year)))
    image_path = os.listdir(path=os.path.join(raw_path, str(year)))
    image_path = [i for i in image_path if not i.startswith('.')]
    # Check whether file has already been read
    text_path = [re.sub('.png', '.txt', i, flags = re.I) for i in image_path]
    text_path = [re.sub('cleaned', 'text', i, flags = re.I) for i in text_path]
    text_path = [os.path.exists(os.path.join(out_path, str(year), t)) is False for t in text_path]
    image_path = list(itertools.compress(image_path, text_path))
    for image in image_path:
        png_to_txt(os.path.join(raw_path, str(year), image), ocr_reader, psm, white_list)


def main(start_year, end_year):
    data_path = '/Volumes/T7/probate_files'
    out_path = os.path.join(data_path, 'text')
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    # ------- NUMBER OF WORKERS = NUMBER OF CORES ----------------
    num_cores = multiprocessing.cpu_count()
    # ------------------------------------------------------------
    inputs = range(start_year, end_year)
    Parallel(n_jobs=num_cores)(delayed(make_per_year)(i, psm, white_list) for i in inputs)


if __name__ == '__main__':
    start_year = int(sys.argv[1].split('=')[1])
    end_year = int(sys.argv[2].split('=')[1])
    psm = int(sys.argv[3].split('=')[1])
    white_list = sys.argv[4].split('=')[1]
    main(start_year, end_year)
