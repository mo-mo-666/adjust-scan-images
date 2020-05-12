import pandas as pd
from collections import defaultdict


def read_metadata(filepath: str):
    with open(filepath, "r") as f:
        csvdata = csv.reader(f)

    metadata = {}
    if len(csvdata) >= 3:



def read_mark_setting(filepath: str, scale: float = None) -> dict:
    with open(filepath, "r") as f:
        csvdata = csv.reader(f)

    marks = defaultdict(dict)
    if len(csvdata) >= 3:
        for row in csvdata[1:]:
            category, value, x, y, r = row
            x, y, r = int(x), int(y), int(r)
            if scale:
                x, y, r = int(x * scale), int(y * scale), int(r * scale)
            marks[category][value] = (x, y, r)
    return dict(marks)
