import csv
from openpyxl import load_workbook
from collections import defaultdict


SETTING_KEYS = {"resize_ratio",
               "is_markread",
               "is_align",
               "marker_gaussian_ksize",
               "marker_gaussian_std",
               "is_marksheet",
               "sheet_gaussian_ksize",
               "sheet_gaussian_std"}


def read_metadata(filepath: str, mode:str="excel", excel_sheet_name:str="image_setting") -> dict:
    """
    Metadata setting loader.

    Parameters
    ----------
    filepath : str
        Setting file path.
    mode : str, optional
        Mode, by default "excel"
    excel_sheet_name : str, optional
        Excel sheet name, by default "image_setting"

    Returns
    -------
    dict
        Metadata.
    """
    wb = load_workbook(filepath, read_only=True)
    ws = wb[excel_sheet_name]
    metadata = {}
    setting_keys = set()
    for row in ws.iter_rows(min_row=3):
        metadata[row[0].value] = row[1].value
        setting_keys += row[0].value

    # chack all SETTING_KEYS is in the setting.
    key_diff = SETTING_KEYS - setting_keys
    if key_diff:
        raise KeyError(f"The key {key_diff} is not found in {filepath}.")

    # scale change
    scale = metadata["resize_ratio"]
    metadata["marker_gaussian_ksize"] = int(metadata["marker_gaussian_ksize"] * scale)
    metadata["marker_gaussian_std"] = int(metadata["marker_gaussian_std"] * scale)
    metadata["sheet_gaussian_ksize"] = int(metadata["sheet_gaussian_ksize"] * scale)
    metadata["sheet_gaussian_std"] = int(metadata["sheet_gaussian_std"]* scale)
    return metadata


def read_mark_setting(filepath: str, scale: float = None, mode:str="excel", excel_sheet_name:str="marksheet") -> dict:
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
        category, value, x, y, r = row
        category, value, x, y, r = category.value, value.value, x.value, y.value, r.value
        x, y, r = int(x), int(y), int(r)
        # scale change
        if scale:
            x, y, r = int(x * scale), int(y * scale), int(r * scale)
        marks[category][value] = (x, y, r)
    return dict(marks)
