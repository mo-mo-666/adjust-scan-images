from openpyxl import load_workbook
from collections import defaultdict
import logging
from typing import Union, Iterable

logger = logging.getLogger("adjust-scan-images")


def read_marksheet_setting(
    filepath: str,
    categories: Union[None, Iterable[str]] = ["labo"],
    pt2px: float = 1,
    **kargs,
) -> dict:
    wb = load_workbook(filepath, read_only=True)
    if not categories:
        return {}

    marks = defaultdict(dict)
    for category in categories:
        r = wb.defined_names
        range = wb.defined_names[category].destinations
        if not range:
            continue
        cells = [wb[s][r] for s, r in range]
        for row in cells:
            data = [r.value for r in row]
            assert (
                len(data) == 5
            ), f"The excel data length of {data} is {len(data)} != 5. The format must be (value, x1, y1, x2, y2) for each row."
            value, x1, y1, x2, y2 = data
            x1, y1, x2, y2 = [int(float(z) * pt2px) for z in (x1, y1, x2, y2)]
            marks[category][value] = (x1, y1, x2, y2)

    return dict(marks)
