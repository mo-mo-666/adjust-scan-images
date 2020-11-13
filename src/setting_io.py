import csv
from openpyxl import load_workbook
from collections import defaultdict
import logging
from typing import Iterable, Optional

logger = logging.getLogger("adjust-scan-images")


SETTING_KEYS_DEFAULT = {
    "resize_ratio": 1,  # float 0 < resize_ratio <= 1.
    "coord_unit": "pt",  # "pt" | "px"
    "is_align": 1,  # 0 | 1
    "marker_range": 200 / 300 * 72,  # float, px
    "marker_gaussian_ksize": 15,  # int
    "marker_gaussian_std": 3,  # int
    "is_marksheet": 1,  # 0 | 1
    "is_marksheet_fit": 1,  # 0 | 1
    "sheet_coord_style": "bbox",  # "rect" | "bbox" | "circle"
    "sheet_score_threshold": 0,  # float
    "sheet_gaussian_ksize": 15,  # int
    "sheet_gaussian_std": 3,  # int
}


def read_metadata(
    filepath: Optional[str] = None,
    mode: str = "excel",
    excel_sheet_name: str = "image_setting",
    pt2px: Optional[float] = None,
    *args,
    **kargs,
) -> dict:
    """
    Metadata setting loader.

    Parameters
    ----------
    filepath : str | None, optional
        Setting file path, by default None
    mode : str, optional
        Mode, by default "excel"
    excel_sheet_name : str, optional
        Excel sheet name, by default "image_setting"
    pt2px : float | None, optional
        if coord unit is pt, you should set the value dpi, optinal by defalut None

    Returns
    -------
    dict
        Metadata.
    """
    metadata = {}
    if filepath:
        wb = load_workbook(filepath, read_only=True)
        ws = wb[excel_sheet_name]
        for row in ws.iter_rows(min_row=3):
            key, value = row[0].value, row[1].value
            metadata[key] = value

    # put default value
    for key, value in SETTING_KEYS_DEFAULT.items():
        if key not in metadata:
            metadata[key] = value

    # logging
    logger.info(f"Metadata loaded: {metadata}")

    # formatting
    metadata["resize_ratio"] = scale = float(metadata["resize_ratio"])
    metadata["is_marksheet"] = int(metadata["is_marksheet"])
    if metadata.get("coord_unit", "px") == "pt" and pt2px is not None:
        v = int(float((metadata["marker_range"])) * scale * (pt2px * scale) / 72)
    else:
        v = int(float((metadata["marker_range"])) * scale)
    metadata["marker_range"] = (
        (0, 0, v, v),
        (0, -v, v, v),
        (-v, -v, v, v),
        (-v, 0, v, v),
    )
    metadata["is_align"] = int(metadata["is_align"])
    metadata["marker_gaussian_ksize"] = int(
        int(metadata["marker_gaussian_ksize"]) * scale
    )
    metadata["marker_gaussian_std"] = int(int(metadata["marker_gaussian_std"]) * scale)
    metadata["is_marksheet"] = int(metadata["is_marksheet"])
    metadata["is_marksheet_fit"] = int(metadata["is_marksheet_fit"])
    metadata["sheet_score_threshold"] = float(metadata["sheet_score_threshold"])
    metadata["sheet_gaussian_ksize"] = int(
        int(metadata["sheet_gaussian_ksize"]) * scale
    )
    metadata["sheet_gaussian_std"] = int(int(metadata["sheet_gaussian_std"]) * scale)
    logger.debug(f"Metadata formatted: {metadata}")

    return metadata


def read_marksheet_setting(
    filepath: str,
    scale: float = 1,
    mode: str = "excel",
    excel_sheet_name: str = "marksheet",
    *args,
    **kargs,
) -> dict:
    """
    Read Marksheet Setting.

    Parameters
    ----------
    filepath : str
        File path.
    scale : float, optional
        Rescale ratio. This corresponds to resize ratio, by default None
    mode : str, optional
        Mode, by default "excel"
    excel_sheet_name : str, optional
        Excel sheet name, by default "marksheet"

    Returns
    -------
    dict
        Marksheet data.
    """
    wb = load_workbook(filepath, read_only=True)
    ws = wb[excel_sheet_name]
    marks = defaultdict(dict)
    for row in ws.iter_rows(min_row=3):
        category, value, x, y, r = [v.value for v in row]
        x, y, r = int(float(x * scale)), int(float(y * scale)), int(float(r * scale))
        marks[category][value] = (x, y, r)
    marks = dict(marks)
    logger.info(f"marksheet data loaded: {marks}")
    return marks


class MarksheetResultWriter:
    """
    Write the marksheet result to a csv file.
    """

    def __init__(self, filepath: str, header: Iterable[str]):
        """
        Parameters
        ----------
        filepath : str
            Csv file path.
        header : Iterable[str]
            Header.
        """
        self.f = open(filepath, "a", encoding="shift_jis", newline="")
        self.is_open = True
        self.writer = csv.DictWriter(self.f, header, extrasaction="ignore")
        self.writer.writeheader()

    def write_one_dict(self, data: dict):
        """
        Write one row.

        Parameters
        ----------
        data : dict
            Dict[header, value]
        """
        self.writer.writerow(data)

    def close(self):
        """
        Close file.
        """
        self.f.close()
        self.is_open = False
