
import os
from png_to_txt import png_to_txt, PyTessy
import multiprocessing
from joblib import Parallel, delayed

os.environ['OMP_THREAD_LIMIT'] = '1'  # avoid conflicts in thread scheduling


def make_per_year(year):
    """
    Makes output files on a per year basis
    Note: this is the 'outer' parralized loop
    :param year:
    :return: None
    """
    # call PyTessy once per job only, pass it to png_to_txt
    ocrReader = PyTessy()
    # set paths again, easier hack than input args
    data_path = '/Volumes/T7/probate_files'
    raw_path = os.path.join(data_path, 'cleaned')
    out_path = os.path.join(data_path, 'out')
    if not os.path.exists(os.path.join(out_path, str(year))):
        os.mkdir(os.path.join(out_path, str(year)))
    image_path = os.listdir(path=os.path.join(raw_path, str(year)))
    image_path.sort()
    for image in image_path:
        png_to_txt(os.path.join(raw_path, str(year), image), ocrReader)


def main():
    data_path = '/Volumes/T7/probate_files'
    out_path = os.path.join(data_path, 'out')
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    ######### NUMBER OF WORKERS = NUMBER OF CORES ################
    num_cores = multiprocessing.cpu_count()
    ##############################################################
    inputs = range(1858, 1872)  # can also be passed as function or sysargs
    Parallel(n_jobs=num_cores)(delayed(make_per_year)(i) for i in inputs)


if __name__ == '__main__':
    main()
