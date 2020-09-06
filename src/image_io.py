import numpy as np
import PIL
from PIL import Image
import os
import glob
from typing import Union, Tuple, Iterator


def read_image(
    path: str, resize_ratio: Union[float, None] = None
) -> Union[Tuple[None, None], Tuple[np.ndarray, Tuple[int, int]]]:
    """
    Read image by gray scale.

    Parameters
    ----------
    path : str
        File path.

    resize_ratio : float or None

    Returns
    -------
    (None, None) or (img, dpi) : None or (np.ndarray, (int, int))
    """
    try:
        pilimg = Image.open(path).convert("L")  # read as gray scale
    except PIL.UnidentifiedImageError:
        return None, None
    dpi = pilimg.info["dpi"]
    if resize_ratio is not None:
        pilimg = pilimg.resize(
            (int(pilimg.width * resize_ratio), int(pilimg.height * resize_ratio))
        )
        dpi = (int(dpi[0] * resize_ratio), int(dpi[1] * resize_ratio))
    return np.array(pilimg), dpi


def read_images(
    dirname: str, ext: Union[str, None] = None, resize_ratio: Union[float, None] = None
) -> Iterator[Tuple[str, np.ndarray, Tuple[int, int]]]:
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

    for p in paths:
        img, dpi = read_image(p, resize_ratio)
        if img is None:
            continue
        yield p, img, dpi


def save_image(path: str, img: np.ndarray, dpi: Tuple[int, int]):

    pilimg = Image.fromarray(img)
    pilimg.save(path, dpi=dpi)
