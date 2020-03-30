import numpy as np
import cv2


def find_one_marker(binary_img: np.ndarray):

    # find contours
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return (0, 0), 0
    areas = [cv2.contourArea(cnt) for cnt in contours]
    # choose max areas
    max_idx = np.argmax(areas)
    max_cnt = contours[max_idx]
    max_area = areas[max_idx]
    # calculate center of gravity
    M = cv2.moments(max_cnt)
    cx = M['m10'] / M['m00']
    cy = M['m01'] / M['m00']
    return (cx, cy), max_area


def find_markers(img: np.ndarray, img_info: dict) -> list:
    """
    find markers

    Note
    ----------
    img_info must have 'marker_range' key and
    img_info['marker_range'] == (topleft, bottomleft, bottomright, topright).
    topleft == (x, y, width, height).

    Parameters
    ----------
    img : np.ndarray
        [description]
    img_info : dict
        [description]

    Returns
    -------
    markers : np.ndarray
        shape = (3, 2)
    """

    # Gaussian filter
    # TODO parameter setting
    blur = cv2.GaussianBlur(img, (15,15), 3)
    # binary image
    _, binary = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
    markers = []
    marker_areas = []
    for x, y, w, h in img_info["marker_range"]:
        edge = binary[y:y+h, x:x+w]
        (cx, cy), area = find_one_marker(edge)
        cx += x
        cy += y
        markers.append((cx, cy))
        marker_areas.append(area)
    markers = np.array(markers)
    marker_areas = np.array(marker_areas)
    sort_idxs = np.argsort(marker_areas)

    # if two of areas are 0, return False.
    if not marker_areas[sort_idxs[1]]:
        return False
    del_idx = sort_idxs[0]
    # marker sort
    m_idxs = [(del_idx+i) % 4 for i in range(1, 4)]
    return markers[m_idxs]


def align_image(base_markers, img_markers, img):
    h, w = img.shape
    # get Affine transform matrix
    M = cv2.getAffineTransform(img_markers, base_markers)
    # Affine transform
    # 255 is white.
    new_img = cv2.warpAffine(img, M, (h, w), borderValue=255)
    return new_img
