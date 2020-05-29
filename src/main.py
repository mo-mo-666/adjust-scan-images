import os
import pandas as pd

from .setting_io import read_metadata, read_mark_setting
from .image_io import read_image, read_images, save_image
from .align_images import ImageAligner
from .read_marksheet import MarkReader



def save_filepath(save_dir: str, read_filename, value: dict=None):
    save_filename = read_filename
    return os.path.join(save_dir, save_filename)


def pipeline(img_dir: str, metadata_path: str, save_dir: str, baseimg_path: str=None, sheet_path: str=None, is_align: bool=True, is_markread: bool=False):

    metadata = read_metadata(metadata_path)
    resize_ratio = metadata["resize_ratio"]
    if is_markread:
        if not sheet_path:
            raise ValueError(f"You should set 'sheet_path' is not None or 'is_markread is False.")
        sheet_data = read_mark_setting(sheet_path, resize_ratio)
        metadata["sheet"] = sheet_data
        mark_reader = MarkReader(metadata)

    img_iter = read_images(img_dir, resize_ratio)

    # read base image
    baseimg = read_image(baseimg_path)
    if is_align:
        aligner = ImageAligner(metadata)
        aligner.fit(baseimg)

    values = []
    for p, img in img_dir:
        filename = os.path.basename(p)
        try:
            if is_align:
                img = aligner.transform_one(img)
            if is_markread:
                v = mark_reader.read(img)
                v["filename"] = filename
                values.append(v)
            else:
                v = None
        except Exception as err:
            # TODO log writer.
            pass

        # Set your customized filename
        q = save_filepath(save_dir, filename, v)
        save_image(q, img)

    # TODO write values to excel file.
