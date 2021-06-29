
import os
import cv2
import numpy as np
import ruptures as rpt
import re
from datetime import datetime


def filenames(input_path, input_year):
    # Find files
    path = os.path.join('/Volumes/T7/probate_files', input_path, str(input_year))
    file_names = []
    for r, d, f in os.walk(path):
        for file_name in f:
            if '.png' in file_name:
                if '._' not in file_name:
                    file_names.append(os.path.join(r, file_name))
    # Tidy files
    file_names.sort()
    return file_names


def image_size(img, dimensions=(2774, 4498)):
    """
    Ensure that the image dimensions match expected shape so that pixel assumptions are met
    :param img:
    :param dimensions:
    :return: img
    """
    img = cv2.resize(img, dimensions, interpolation=cv2.INTER_AREA)
    return img


def black_on_white(img):
    """
    Tesseract performs poorly with white-on-black text so invert if needed
    :param img:
    :return: img
    """
    # Are more pixels black or white?
    white = len(img[img == 255])
    black = len(img[img == 0])

    # If mostly black, invert image
    if black > white:
        img = cv2.bitwise_not(img)

    return img


def remove_large_blobs(img, blur_size):
    """

    :param img:
    :param blur_size:
    :return:
    """

    """
       a) Blobs bigger than 200 pixels can't be a letter and must be noise so remove
    """
    # Blur image and ensure all pixels are pure black or white
    blur = cv2.GaussianBlur(img, (blur_size, blur_size), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Find contours and draw mask
    counts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    counts = counts[0] if len(counts) == 2 else counts[1]
    mask = np.zeros(img.shape, dtype=np.uint8)

    # For each contour measure size and convert to white if larger than 200 pixels
    for c in counts:
        x, y, w, h = cv2.boundingRect(c)
        if h >= 200:
            cv2.fillPoly(mask, c, [255, 255, 255])

    """
       b) Blobs that are still visible after closing morphology with extreme value (51) can't be a letter so remove
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51))
    res = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    res = cv2.bitwise_not(res)
    img[res == 0] = 255

    """
       c) Finally, search for any outstanding large blobs of black pixels with size of 200+ pixels
    """
    # Blur image and ensure all pixels are pure black or white
    blur = cv2.GaussianBlur(img, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Find contours and draw rectangle
    counts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    counts = counts[0] if len(counts) == 2 else counts[1]

    # For each contour measure size and convert to white if larger than 200 pixels
    for c in counts:
        x, y, w, h = cv2.boundingRect(c)
        if h >= 200:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)

    return img


def find_page_margins(img, padding_size, year):
    """

    :param img:
    :param padding_size:
    :param year:
    :return:
    """
    # Count number of black pixels in each column
    points = np.count_nonzero(img == 0, axis=0)

    # Kernelised mean change
    model = 'rbf'
    algo = rpt.Pelt(model=model).fit(points)
    result = algo.predict(pen=10)

    # Columns up to first local mean = left border
    start = result[0] - padding_size
    if start < 0:
        start = 0

    # Columns in last local mean = right border
    end = result[-2] + padding_size

    # If left margin is less than 100, do nothing
    if year < 1892:
        if start > 100:

            # If average number of black pixels is less than 10
            # if np.average(points[:start]) < 10:
            # Turn all pixels in this range white
            img[:, :start] = 255

        # Don't trim too much from right
        if end - start > 2100:
            # Turn all pixels in this range white
            img[:, end:] = 255

    else:
        img[:, :start] = 255
        img[:, end:] = 255

    return img


def bounding_boxes(img, kernel_size):
    """

    :param img:
    :param kernel_size:
    :return:
    """

    """
       a) Bounding box per line of text: identify vertical lines of text by dilating pixels horizontally. If text, the 
       height will be greater than  30 pixels once stretched. Otherwise, pixels represent noise and should be removed.
    """
    # Blur image and ensure all pixels are pure black or white
    blur = cv2.GaussianBlur(img, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Create rectangular structuring element and dilate
    white_bg = 255 * np.ones_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, 1))
    dilate = cv2.dilate(thresh, kernel, iterations=10)

    # Find contours and draw rectangle
    counts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    counts = counts[0] if len(counts) == 2 else counts[1]

    # If height of bounding box is greater than 30 then keep
    for c in counts:
        x, y, w, h = cv2.boundingRect(c)
        roi = img[y:y + h, x:x + w]
        if h >= 30:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    """
       b) Bounding box per paragraph: identify vertical lines of text by dilating pixels horizontally and vertically 
       (rectangle). If text, the width will be greater than 80 pixels.
    """
    # Vertical
    white_bg = 255 * np.ones_like(img)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 4))
    dilate = cv2.dilate(thresh, kernel, iterations=11)

    # Find contours and draw rectangle
    counts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    counts = counts[0] if len(counts) == 2 else counts[1]

    # If width of bounding box is greater than 80 then keep
    for c in counts:
        x, y, w, h = cv2.boundingRect(c)
        roi = img[y:y + h, x:x + w]
        if w > 80:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 1)
            white_bg[y:y + h, x:x + w] = roi

    img = white_bg

    """
       c) Bounding box per page: identify the limits to each page and remove points outside of this space. 
    """
    # Find one contour
    median = cv2.medianBlur(img, 21)
    thresh = cv2.threshold(
        median, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Dilate image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    dilate = cv2.dilate(thresh, kernel, iterations=7)

    # Find contours
    counts, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    counts = [c for c in counts if (cv2.boundingRect(c)[0] > 0)]
    counts = [c for c in counts if (cv2.boundingRect(c)[1] > 0)]
    counts = [c for c in counts if (cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] < img.shape[1])]
    counts = [c for c in counts if (cv2.boundingRect(c)[1] + cv2.boundingRect(c)[3] < img.shape[0])]

    # Concatenate all contours
    counts = np.concatenate(counts)

    # Determine and draw bounding rectangle
    x, y, w, h = cv2.boundingRect(counts)
    mask = 255 * np.ones_like(img)
    mask[y:y + h, x:x + w] = img[y:y + h, x:x + w]

    img = mask

    return img


def remove_speckles(img):
    """
    Remove all contours that are too small to be a letter or part of a letter (e.g., dot above the letter i)
    :param img:
    :return: img
    """

    # Ensure that image is black and white
    _, black_and_white = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    # Find connected components and sizes
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        black_and_white, None, None, None, 8, cv2.CV_32S
    )
    sizes = stats[1:, -1]

    # If size is less than 30 pixels then noise; don't copy to img2
    for j in range(0, n_labels - 1):

        if sizes[j] < 3:
            img[labels == j + 1] = 255

    return img


def deskew(img):
    """
    Ensure tha the margins are parallel to the page border
    :param img:
    :return: img
    """
    # Blur image
    coords = np.column_stack(np.where(img == 0))
    angle = cv2.minAreaRect(coords)[-1]

    # If angle is flush (e.g., 90) then do nothing
    if angle % 90 != 0:
        # If angle is greater than 45 then find the acute angle
        if angle > 45:
            angle = -(90 - angle)
        # Otherwise invert angle
        else:
            angle = -angle

        # If angle is large then do nothing (potential miscalculation)
        if abs(angle) < 1:
            # Rotate the image to de-skew it
            (h, w) = img.shape[:2]
            center = (w // 2, h // 2)
            m = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img, m, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=255
            )

    return img


def resize(img, optimal):
    """
    Some images should be resized to optimise the accuracy of Tesseract
    Note: params learned from the random sampling of pages and accuracy detection
    :param img:
    :param optimal:
    :return: img
    """

    # If already optimal do nothing
    if optimal != 100:
        # Else reshape according to optimal size
        width = int(img.shape[1] * optimal / 100)
        height = int(img.shape[0] * optimal / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        ret, img = cv2.threshold(img, 177, 255, cv2.THRESH_BINARY)

    return img


def clean_file(file, blur_size, padding_size, year, kernel_size, optimal, i, o):
    """
    Cleans file according to params that are specific to the year of record.
    :param o:
    :param i:
    :param optimal:
    :param kernel_size:
    :param year:
    :param padding_size:
    :param blur_size:
    :param file:
    :return: None
    """

    # Read in image
    img = cv2.imread(file, 0)

    # Standardise image size
    img = image_size(img)

    # Ensure that image contains black text on white background
    img = black_on_white(img)

    # Removes large ink blobs
    img = remove_large_blobs(img, blur_size)

    # Remove annotations from page margins
    img = find_page_margins(img, padding_size, year)

    # Clean pixels outside of text bounding boxes
    img = bounding_boxes(img, kernel_size)

    # Drop tiny speckles of dust
    img = remove_speckles(img)

    # Straighten image
    # img = deskew(img)

    # Resize image
    img = resize(img, optimal)

    # Save file
    dest = re.sub(i, o, file)
    cv2.imwrite(dest, img)

    # Optional progress update
    print(dest + ' complete at ' + datetime.now().strftime("%H:%M:%S"))
