import os
import csv

from .setting_io import read_metadata, read_mark_setting
from .image_io import read_image, read_images, save_image
from .align_images import ImageAligner
from .read_marksheet import MarkReader



def save_filepath(save_dir: str, read_filename: str, value: dict=None):
    save_filename = read_filename
    if value:
        pass
    return os.path.join(save_dir, save_filename)


def pipeline(img_dir: str, metadata_path: str, save_dir: str, baseimg_path: str):

    metadata = read_metadata(metadata_path)
    resize_ratio = metadata["resize_ratio"]
    is_align = metadata["is_align"]
    is_markread = metadata["is_markread"]
    if is_markread:
        metadata["sheet"] = read_mark_setting(metadata_path, resize_ratio)
        mark_reader = MarkReader(metadata)

    img_iter = read_images(img_dir, resize_ratio)

    # read base image
    baseimg = read_image(baseimg_path)
    if is_align:
        aligner = ImageAligner(metadata)
        aligner.fit(baseimg)

    values = []
    for p, img in img_iter:
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
