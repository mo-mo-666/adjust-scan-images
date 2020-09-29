import numpy as np
import cv2
import logging
from typing import Union

logger = logging.getLogger("adjust-scan-images")


class MarkReader:
    """
    Mark Sheet Reader.

    Note
    ----------
    IMAGES MUST HAVE BEEN ALREADY ADJUSTED.
    metadata must have 'sheet' key and 'sheet_gaussian' key.

    When coord_style == "rect",
    metadata['sheet'] == {category1: {value1: (x1, y1, x2, y2), value2: (x1, y1, x2, y2),...}, category2: {...},...},
    where (x1, y1) is the top-left coord and (x2, y2) is the bottom-right coord.
    When coord_style == "bbox",
    metadata['sheet'] == {category1: {value1: (x, y, w, h), value2: (x, y, w, h),...}, category2: {...},...},
    where w and h mean width and height respectively.
    When coord_style == "circle",
    metadata['sheet'] == {category1: {value1: (x, y, r), value2: (x, y, r),...}, category2: {...},...}.

    metadata['sheet_gaussian_ksize'] == int.
    metadata['sheet_gaussian_std] == int.
    """

    def __init__(self, metadata: dict, coord_style: str = "circle"):
        """
        Parameters
        ----------
        metadata : dict
            Image metadata. See Note.
        coord_style : "rect" | "circle"
            Specify metadata style. See Note.
        """
        self.metadata = metadata
        self.sheet = self.metadata["sheet"]
        self.is_sheet = bool(self.sheet)
        self.coord_style = coord_style
        if not self.is_sheet:
            logger.warn("There are not marksheet datas.")
        if self.coord_style == "rect":
            self.sheet = self.__rect2bbox(self.sheet)
        if self.coord_style == "circle":
            self.sheet = self.__circle2bbox(self.sheet)
        self.g_ksize = self.metadata["sheet_gaussian_ksize"]
        self.g_std = self.metadata["sheet_gaussian_std"]
        self.is_fitted = False
        self.base_scores = None

    def __rect2bbox(self, sheet_metadata: dict):
        rect_dict = {}
        for category, values in sheet_metadata.items():
            new_values = {}
            for value, (x1, y1, x2, y2) in values.items():
                new_values[value] = (x1, y1, x2 - x1, y2 - y1)
            rect_dict[category] = new_values
        return rect_dict

    def __circle2bbox(self, sheet_metadata: dict):
        rect_dict = {}
        for category, values in sheet_metadata.items():
            new_values = {}
            for value, (x, y, r) in values.items():
                new_values[value] = (max(x - r, 0), max(y - r, 0), 2 * r, 2 * r)
            rect_dict[category] = new_values
        return rect_dict

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Image preprocess to read mark sheet.

        Parameters
        ----------
        img : np.ndarray
            An image.

        Returns
        -------
        np.ndarray
            The processed image.
        """
        blur = cv2.GaussianBlur(img, (self.g_ksize, self.g_ksize), self.g_std)
        preprocessed = cv2.bitwise_not(blur)
        logger.debug("MarkReader: Preprocess ended.")
        return preprocessed

    def _one_mark_score(
        self, img: np.ndarray, coords: dict, base_score: Union[dict, None] = None
    ) -> dict:
        scores = {}
        ih, iw = img.shape
        for value, (x, y, w, h) in coords.items():
            score = np.mean(img[y : min(y + h, ih), x : min(x + w, iw)])
            if base_score is not None:
                score -= base_score[value]
            scores[value] = score
        return scores

    def _one_mark(
        self, img: np.ndarray, coords: dict, base_score: Union[dict, None] = None
    ) -> str:
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
        score_dict = self._one_mark_score(img, coords, base_score)
        logger.debug(f"Marksheet scores: {score_dict}")
        values, scores = tuple(coords.keys()), tuple(coords.values())
        idx = np.argmax(scores)
        value = values[idx]
        logger.debug(f"Chosen value: {value}")
        return value

    def fit(self, img: np.ndarray):
        if not self.is_sheet:
            logger.debug("MarkReader: Fit skipped since there is no marksheet data.")
            return None
        preprocessed = self._preprocess(img)
        self.base_scores = {}
        for category, coords in self.sheet.items():
            score_dict = self._one_mark_score(preprocessed, coords)
            self.base_scores[category] = score_dict
        logger.debug(f"ImageAligner: Fit is completed, base_scores: {self.base_scores}")
        self.is_fitted = True

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
        if not self.is_sheet:
            logger.debug("MarkReader: Read skipped since there is no marksheet data.")
            return {}
        preprocessed = self._preprocess(img)
        mark = {}
        for category, coords in self.sheet.items():
            if self.is_fitted:
                value = self._one_mark(preprocessed, coords, self.base_scores[category])
            else:
                value = self._one_mark(preprocessed, coords)
            mark[category] = value
        logger.debug(f"Mark read result: {mark}")
        return mark
