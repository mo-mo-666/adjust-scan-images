import os
import datetime
from typing import Union


NOW = datetime.datetime.now()
NOW = f"{NOW.year}{NOW.month:02}{NOW.day:02}{NOW.hour:02}{NOW.minute:02}{NOW.second:02}"


SETTING_KEYS_DEFAULT = {
    "resize_ratio": 1,
    "is_align": 1,
    "marker_range": 200,
    "marker_gaussian_ksize": 15,
    "marker_gaussian_std": 3,
    "is_marksheet": 1,
    "is_marksheet_fit": 1,
    "sheet_coord_style": "rect",
    "sheet_gaussian_ksize": 15,
    "sheet_gaussian_std": 3,
}


def decide_save_filepath(
    read_path: str, save_dir: str, data: Union[dict, None] = None
) -> str:
    """
    Decide file name when saving an image. OVERRIDE THIS TO CHANGE THE FILENAME.

    Parameters
    ----------
    read_filename : str
        Original file path.
    data : Union[dict, None], optional
        The data used by deciding the file name, by default None

    Returns
    -------
    str
        Save file path.
    """
    read_filename = os.path.basename(read_path)
    read_dir = os.path.dirname(read_path)
    if data:
        _, ext = os.path.splitext(read_filename)
        save_filename = f"{read_dir}-{data.get('dirname', 'x')}_{data.get('room', 'x')}_{data.get('class', 'x')}_{data.get('student_number_10', 'x')}{data.get('student_number_1','x')}{ext}"
    else:
        save_filename = read_filename
    return os.path.join(save_dir, save_filename)
