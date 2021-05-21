import numpy as np
import cv2
import logging
from typing import Tuple

from .errors import MarkerNotFoundError, NotFittedError

logger = logging.getLogger("adjust-scan-images")


class ImageAligner:
    """
    Image Aligner.

    Note
    ----------
    metadata must have 'marker_ranges' key and 'marker_gaussian' key.

    metadata['marker_range'] == (topleft, bottomleft, bottomright, topright).
    topleft == (x, y, width, height).
    metadata['marker_gaussian_ksize'] == int.
    metadata['marker_gaussian_std'] == int.
    """

    def __init__(self, metadata: dict):
        """
        Image aligner constractor.

        Parameters
        ----------
        metadata : dict
            Image metadata. See Note.
        """
        self.metadata = metadata
        self.g_ksize = self.metadata["marker_gaussian_ksize"]
        self.g_std = self.metadata["marker_gaussian_std"]
        self.marker_ranges = self.metadata["marker_range"]
        assert (
            len(self.marker_ranges) == 4
        ), "metadata['marker_ranges'] does not satisfy the precise format."
        self.base_markers = None
        self.is_fitted = False

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Gaussian filtering and image Binarization.

        Parameters
        ----------
        img : np.ndarray

        Returns
        -------
        binary : np.ndarray
            Binary image.
        """
        # Gaussian filter
        blur = cv2.GaussianBlur(img, (self.g_ksize, self.g_ksize), self.g_std)
        # binary image
        _, binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
        logger.debug("ImageAliger: Preprocess ended.")
        return binary

    def __find_one_marker(
        self, binary_img: np.ndarray
    ) -> Tuple[Tuple[float, float], float]:
        """
        Find single marker.

        Parameters
        ----------
        binary_img : np.ndarray
            binary image.

        Returns
        -------
        (cx, cy), max_area
            marker information.
        """
        # find contours
        contours, _ = cv2.findContours(
            binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return (0, 0), 0
        areas = [cv2.contourArea(cnt) for cnt in contours]
        # choose maximum area
        max_idx = np.argmax(areas)
        max_cnt = contours[max_idx]
        max_area = areas[max_idx]
        # calculate center of gravity
        M = cv2.moments(max_cnt)
        try:
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            return (cx, cy), max_area
        except ZeroDivisionError:
            return (0, 0), 0

    def _find_markers(self, binary_img: np.ndarray) -> np.ndarray:
        """
        Find markers.

        Parameters
        ----------
        binary_img : np.ndarray
            A binary image.

        Returns
        -------
        markers : np.ndarray
            shape == (3, 2)
        """
        markers = []
        marker_areas = []
        bh, bw = binary_img.shape
        for x, y, w, h in self.marker_ranges:
            # If x or y is negative, change positive.
            if x < 0:
                x += bw
            if y < 0:
                y += bh

            edge = binary_img[y : min(y + h, bh), x : min(x + w, bw)]
            (cx, cy), area = self.__find_one_marker(edge)
            cx += x
            cy += y
            markers.append((cx, cy))
            marker_areas.append(area)
        markers = np.array(markers)
        marker_areas = np.array(marker_areas)
        sort_idxs = np.argsort(marker_areas)
        logger.debug(f"Raw markers: {markers}")
        logger.debug(f"Areas: {marker_areas}")

        # if two of areas are 0, return False.
        if not marker_areas[sort_idxs[1]]:
            return False
        del_idx = sort_idxs[0]
        # marker sort
        m_idxs = [(del_idx + i) % 4 for i in range(1, 4)]
        markers = markers[m_idxs]
        return markers

    def _align_image(
        self, base_markers: list, img_markers: list, img: np.ndarray
    ) -> np.ndarray:
        """
        Aline images.

        Parameters
        ----------
        base_markers : list = [int, int, int]
            Coordinate of markers of base images.

        img_markers : list = [int, int, int]
            Coordinate of markers of base images.

        img : np.ndarray
            An image.

        Returns
        -------
        np.ndarray
            An aligned image.
        """
        h, w = img.shape
        # get Affine transform matrix
        logger.debug(f"Begin Affine transform:{img_markers} -> {base_markers}")
        M = cv2.getAffineTransform(np.float32(img_markers), np.float32(base_markers))
        # Affine transform
        # 255 is white.
        new_img = cv2.warpAffine(img, M, (w, h), borderValue=255)
        return new_img

    def fit(self, img: np.ndarray):
        """
        Create base.

        Parameters
        ----------
        img : np.ndarray
            A base image.

        Raises
        ------
        MarkerNotFoundError
        """
        binary = self._preprocess(img)
        self.base_markers = self._find_markers(binary)
        if self.base_markers is False:
            raise MarkerNotFoundError("We cannot find the markers in the base image.")
        self.is_fitted = True
        logger.debug(
            f"ImageAligner: Fit is completed, base_markers: {self.base_markers}"
        )

    def transform_one(self, img: np.ndarray) -> np.ndarray:
        """
        Transform one image.

        Parameters
        ----------
        img : np.ndarray
            One image.

        Returns
        -------
        np.ndarray
            An aligned image.

        Raises
        ------
        MarkerNotFoundError
        """
        if not self.is_fitted:
            raise NotFittedError("Fit before trasform.")

        binary = self._preprocess(img)
        markers = self._find_markers(binary)
        if markers is False:
            raise MarkerNotFoundError("We cannot find the markers in the image.")
        new_img = self._align_image(self.base_markers, markers, img)
        return new_img
