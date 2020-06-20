import csv
from openpyxl import load_workbook
from collections import defaultdict


SETTING_KEY = ["resize_ratio",
               "is_markread",
               "marker_range",
               "marker_gaussian_ksize",
               "marker_gaussian_std",
               "is_sheet",
               "sheet_gaussian_ksize",
               "sheet_gaussian_std"]


def read_metadata(filepath: str, mode:str="excel", excel_sheet_name:str="image_setting") -> dict:
    wb = load_workbook(filepath, read_only=True)
    ws = wb[excel_sheet_name]
    metadata = {}
    for row in ws.iter_rows(min_row=3):
        metadata[row[0].value] = row[1].value
    return metadata


def read_mark_setting(filepath: str, scale: float = None, mode:str="excel", excel_sheet_name:str="marksheet") -> dict:
    wb = load_workbook(filepath, read_only=True)
    ws = wb[excel_sheet_name]
    marks = defaultdict(dict)
    for row in ws.iter_rows(min_row=3):
        category, value, x, y, r = row
        category, value, x, y, r = category.value, value.value, x.value, y.value, r.value
        x, y, r = int(x), int(y), int(r)
        if scale:
            x, y, r = int(x * scale), int(y * scale), int(r * scale)
        marks[category][value] = (x, y, r)
    return dict(marks)
