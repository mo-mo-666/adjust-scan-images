import os
import logging
from typing import Optional, List, Tuple

from .setting_io import MarksheetResultWriter
from .setting_io_ds import read_metadata, read_marksheet_setting, decide_save_filename
from .image_io import read_image, read_images, ImageSaver
from .align_images import ImageAligner
from .read_marksheet import MarkReader
from .errors import MarkerNotFoundError
from .const import NOW


logger = logging.getLogger("adjust-scan-images")


def pipeline(
    img_dir: str, metadata_path: Optional[str], save_dir: str, baseimg_path: str
):
    """
    Process pipeline.

    Parameters
    ----------
    img_dir : str
        The name of the directory. We read the images in this directory.
    metadata_path : None | str
        The path of the metadata.
    save_dir : str
        The name of the directory. We save the processed images in this directory.
    baseimg_path : str
        The base image for the transformation.
    """

    # log for parameters
    logger.info(f"img_dir: {img_dir}")
    logger.info(f"metadata_path: {metadata_path}")
    logger.info(f"save_dir: {save_dir}")
    logger.info(f"baseimg_path: {baseimg_path}")

    # read metadata
    # metadata = read_metadata(metadata_path, pt2px = dpi[0])
    baseimg, dpi = read_image(baseimg_path)
    metadata = read_metadata(metadata_path, pt2px=dpi[0])
    resize_ratio: float = metadata["resize_ratio"]
    is_align: bool = metadata["is_align"]
    is_marksheet: bool = metadata["is_marksheet"]
    is_marksheet_fit: bool = metadata["is_marksheet_fit"]
    coord_unit = metadata["coord_unit"]
    pt2px: Optional[int] = dpi[0] if coord_unit == "pt" else None

    # read base image
    logger.debug(f"Begin reading the base image {baseimg_path}")
    baseimg, dpi = read_image(baseimg_path, resize_ratio=resize_ratio)
    if baseimg is None:
        logger.error(f"The file {baseimg_path} is not an image.")
        raise FileExistsError(f"The file {baseimg_path} is not an image.")

    # marksheet setting
    if is_marksheet:
        logger.debug(f"is_marksheet == 1")
        metadata["sheet"] = read_marksheet_setting(
            metadata_path, resize_ratio, pt2px=pt2px
        )
        mark_reader = MarkReader(metadata)
        marksheet_result_path = os.path.join(save_dir, f"marksheet_result_{NOW}.csv")
        logger.info(f"Marksheet result is saved at {marksheet_result_path}")
        marksheet_result_header = tuple(
            ["origin_filename", "save_filename"] + list(metadata["sheet"].keys())
        )
        marksheet_result_writer = MarksheetResultWriter(
            marksheet_result_path, marksheet_result_header
        )
    else:
        logger.debug(f"is_marksheet == 0")

    # fit base image
    if is_align:
        aligner = ImageAligner(metadata)
        aligner.fit(baseimg)
    if is_marksheet and is_marksheet_fit:
        mark_reader.fit(baseimg)

    img_iter = read_images(img_dir, resize_ratio=resize_ratio)
    error_paths: List[Tuple[str, str]] = []
    image_saver = ImageSaver(save_dir)
    for p, img, dpi in img_iter:
        is_error = False
        logger.debug(f"Begin processing for {p}")
        filename = os.path.basename(p)
        if is_align:
            try:
                img = aligner.transform_one(img)
            except MarkerNotFoundError:
                logger.error(
                    f"The image '{p}' cannot be aligned since we cannot find markers."
                )
                is_error = True
        if is_marksheet:
            v = mark_reader.read(img)
            nonekey = [k_ for k_, v_ in v.items() if v_ is None]
            if nonekey:
                logger.warn(f"We cannot find the following marksheet check: {nonekey}")
                is_error = True
            v["origin_filename"] = filename
        else:
            v = None

        # Set your customized filename
        save_filename = decide_save_filename(p, save_dir, v)
        save_filename = image_saver.save(save_filename, img, dpi)
        logger.info(f"{p} -> {os.path.join(save_dir, save_filename)} saved.")
        if is_marksheet:
            v["save_filename"] = save_filename
            marksheet_result_writer.write_one_dict(v)
        if is_error:
            error_paths.append((filename, save_filename))

    # error summary
    if error_paths:
        error_summary = ""
        for ep in error_paths:
            error_summary += f"{ep}\n"
        logger.warn(
            f"ERROR SUMMARY: The following files occurred some error (original_filename, save_filename).:\n{error_summary}"
        )

    if is_marksheet:
        marksheet_result_writer.close()
