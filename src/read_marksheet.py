import numpy as np
import cv2


class MarkReader:
    """
    Mark Sheet Reader.

    Note
    ----------
    IMAGES MUST HAVE BEEN ALREADY ADJUSTED.
    metadata must have 'sheet' key and 'sheet_gaussian' key.

    metadata['sheet'] == {category1: {value1: (x, y, r), value2: (x, y, r),...}, category2: {...},...}.
    metadata['sheet_gaussian_ksize'] == int.
    metadata['sheet_gaussian_std] == int.
    """
    def __init__(self, metadata: dict):
        """
        Mark reader constractor.

        Parameters
        ----------
        metadata : dict
            Image metadata. See Note.
        """
        self.metadata = metadata
        self.sheet = self.metadata["sheet"]
        self.g_ksize = self.metadata["sheet_gaussian_ksize"]
        self.g_std = self.metadata["sheet_gaussian_std"]

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Image preprocess to read mark sheet.

        Parameters
        ----------
        img : np.ndarray
            An image

        Returns
        -------
        np.ndarray
            The processed image.
        """
        blur = cv2.GaussianBlur(img, (self.g_ksize, self.g_ksize), self.g_std)
        preprocessed = cv2.bitwise_not(blur)
        return preprocessed

    def _one_mark(self, img: np.ndarray, coords: dict) -> str:
        """
        Read one category.

        Parameters
        ----------
        img : np.ndarray
            An image.

        coords : dict
            The place of marks.

        Returns
        -------
        str
            A value.
        """
        values = coords.keys()
        ih, iw = img.shape
        scores = [np.mean(img[max(y-r, 0):min(y+r, ih), max(x-r, 0):min(x+r, iw)]) for x, y, r in coords.values()]
        idx = np.argmax(scores)
        return values[idx]

    def read(self, img: np.ndarray) -> dict:
        """
        Read marks of an image.

        Parameters
        ----------
        img : np.ndarray
            An image.

        Returns
        -------
        dict
            Values.
        """
        preprocessed = self._preprocess(img)
        mark = {}
        for category, coords in self.sheet.items():
            value = self._one_mark(preprocessed, coords)
            mark[category] = value
        return mark
