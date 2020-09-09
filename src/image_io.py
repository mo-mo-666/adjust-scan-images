import numpy as np
import PIL
from PIL import Image
import os
import glob
from typing import Union, Tuple, Iterator
import logging

from numpy.core.fromnumeric import resize

logger = logging.getLogger("adjust-scan-images")


def read_image(
    path: str, resize_ratio: Union[float, None] = None
) -> Union[Tuple[None, None], Tuple[np.ndarray, Tuple[int, int]]]:
    """
    Read image in grayscale.

    Parameters
    ----------
    path : str
        File path.
    resize_ratio : float or None
        Resize ratio. 0 < resize_ratio <= 1.

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
    Iterator of (path, image, dpi).
    """
    if ext:
        pathr = os.path.join(dirname, "**", "*" + ext)
    else:
        pathr = os.path.join(dirname, "**")
    # search
    paths = sorted(glob.glob(pathr, recursive=True))
    # exclude directory name
    paths = [p for p in paths if os.path.isfile(p)]
    filenum = len(paths)
    logger.debug(f"We detected {filenum} files in {dirname}.")

    for i, p in enumerate(paths, start=1):
        logger.info(f"{i}/{filenum};;; Begin processing for {p} {'-'*100}")
        img, dpi = read_image(p, resize_ratio)
        if img is None:
            logger.debug(f"{p} is not an image (skipped).")
            continue
        yield p, img, dpi


class ImageSaver:
    """
    Image saver.
    """

    def __init__(self, dirname: str):
        """
        Parameters
        ----------
        dirname : str
            The directory name where we save the images.
        """
        self.dirname = dirname
        self.filenames = set()
        os.makedirs(dirname, exist_ok=True)

    def _save_image(self, filename: str, img: np.ndarray, dpi: Tuple[int, int]):
        """
        Save an image.

        Parameters
        ----------
        filename : str
            File name. We save the images to the path 'dirname/filename'.
        img : np.ndarray
            An image.
        dpi : Tuple[int, int]
            dpi.
        """
        path = os.path.join(self.dirname, filename)
        pilimg = Image.fromarray(img)
        pilimg.save(path, dpi=dpi)

    def _retain_identity(self, filename: str) -> str:
        """
        To retain identity.

        Parameters
        ----------
        filename : str
            Original file name.

        Returns
        -------
        str
            Transformed file name.
        """
        if filename not in self.filenames:
            self.filenames.add(filename)
            return filename
        name, ext = os.path.splitext(filename)
        tail = 2
        while True:
            filename = f"{name}-{tail}{ext}"
            if filename not in self.filenames:
                self.filenames.add(filename)
                return filename
            tail += 1

    def save(self, filename: str, img: np.ndarray, dpi: Tuple[int, int]) -> str:
        """
        Save image.

        Parameters
        ----------
        filename : str
             Original file name.
        img : np.ndarray
            An image.
        dpi : Tuple[int, int]
            dpi.

        Returns
        -------
        str
            Saved file name.
        """
        filename_ = self._retain_identity(filename)
        if filename_ != filename:
            logger.info(
                f"The file name changed to retain identity. {filename} -> {filename_}"
            )
        self._save_image(filename_, img, dpi)
        return filename
