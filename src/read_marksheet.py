import numpy as np
import cv2


class MarkReader:

    def __init__(self, metadata):
        self.metadata = metadata
        self.sheet = self.metadata["sheet"]
        self.g_ksize, self.g_std = self.metadata["sheet_gaussian"]

    def _preprocess(self, img):

        blur = cv2.GaussianBlur(img, (self.g_ksize, self.g_ksize), self.g_std)
        preprocessed = cv2.bitwise_not(blur)
        return preprocessed

    def _one_mark(self, img, coords):
        values = coords.keys()
        scores = [np.mean(img[y-r:y+r, x-r:x+r]) for x, y, r in coords.values()]
        idx = np.argmax(scores)
        return values[idx]

    def read(self, img):
        preprocessed = self._preprocess(img)
        mark = {}
        for category, coords in self.sheet.items():
            value = self._one_mark(preprocessed, coords)
            mark[category] = value
        return mark
