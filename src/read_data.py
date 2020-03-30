import cv2
import os
import glob
import tqdm


def read_image(path:str, resize_ratio:float=None) -> np.ndarray:
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


def read_images(dirname: str, ext: str=None) -> iterator:
    """
    Read images and return iterator.

    Parameters
    ----------
    dirname: str
        name of the directory.
    ext: str or None
        file's extension such as ".png", ".jpg",...

    Returns
    ----------
    iterator of (path, image).
    """
    if ext:
        pathr = os.path.join(dirname, "**", "*"+ext)
    else:
        pathr = os.path.join(dirname, "**")
    # search
    paths = glob.glob(pathr, recursive=True)
    # exclude directory name
    paths = [p for p in paths if os.path.isfile(p)]
    for p in tqdm.tqdm(paths):
        img = read_image(p)
        if img is None:
            continue
        yield p, img
