import csv
from collections import defaultdict


def read_adjust_setting(filepath):



def read_mark_setting(filepath, scale: float = None) -> dict:
    with open(filepath, "r") as f:
        csvdata = csv.reader(f)

    marks = defaultdict(dict)
    if len(csvdata) >= 1:
        for row in csvdata[1:]:
            category, value, x, y, r = row
            x, y, r = int(x), int(y), int(r)
            if scale:
                x, y, r = x // scale, y // scale, r // scale
            marks[category][value] = (x, y, r)
    return marks
