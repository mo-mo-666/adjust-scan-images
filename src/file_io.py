import numpy as np
import cv2
import os
import glob
import tqdm


def read_image(path: str, resize_ratio: float = None) -> np.ndarray:
    """
    Read image by gray scale.

    Parameters
    ----------
    path : str
        File path.

    resize_ratio : float or None

    Returns
    -------
    img : np.ndarray
    """
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if resize_ratio:
        img = cv2.resize(img, None, fx=resize_ratio, fy=resize_ratio)
    return img


def read_images(dirname: str, ext: str = None, resize_ratio: float = None):
    """
    Read images and return iterator.

    Parameters
    ----------
    dirname: str
        Name of the directory.
    ext: str or None
        File's extension such as ".png", ".jpg",...

    Returns
    ----------
    Iterator of (path, image).
    """
    if ext:
        pathr = os.path.join(dirname, "**", "*" + ext)
    else:
        pathr = os.path.join(dirname, "**")
    # search
    paths = sorted(glob.glob(pathr, recursive=True))
    # exclude directory name
    paths = [p for p in paths if os.path.isfile(p)]
    # tqdm is for a progress bar.
    for p in tqdm.tqdm(paths):
        img = read_image(p, resize_ratio)
        if img is None:
            continue
        yield p, img


def save_image(path: str, img: np.ndarray):
    """
    Save one image.

    Parameters
    ----------
    path : str
        A path.

    img : np.ndarray
        An image.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)
