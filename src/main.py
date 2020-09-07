import os
import time
import datetime
import argparse
import logging
from typing import Tuple, Union

from .setting_io import read_metadata, read_mark_setting, MarksheetResultWriter
from .image_io import read_image, read_images, ImageSaver
from .align_images import ImageAligner
from .read_marksheet import MarkReader
from .log_setting import set_logger
from .errors import MarkerNotFoundError

NOW = datetime.datetime.now()
NOW = f"{NOW.year}{NOW.month:02}{NOW.day:02}{NOW.hour:02}{NOW.minute:02}{NOW.second:02}"

logger = logging.getLogger("adjust-scan-images")


def decide_save_filename(read_filename: str, data: Union[dict, None] = None):
    save_filename = read_filename
    if data:
        _, ext = os.path.splitext(read_filename)
        save_filename = f"{data.get('room', 'x')}_{data.get('class', 'x')}_{data.get('student_number_10', 'x')}{data.get('student_number_1','x')}{ext}"
    return save_filename


def setup_logger(console_mode: int, save_dir: str, file_mode: int):
    # log setting
    os.makedirs(save_dir, exist_ok=True)
    logpath = os.path.join(save_dir, f"log_{NOW}.txt")
    set_logger(console_mode, logpath, file_mode)
    logger.info(f"Log saving at {logpath}.")


def pipeline(img_dir: str, metadata_path: str, save_dir: str, baseimg_path: str):
    """
    Process pipeline.

    Parameters
    ----------
    img_dir : str
        The name of the directory. We read the images in this directory.
    metadata_path : str
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
    metadata = read_metadata(metadata_path)

    resize_ratio = metadata["resize_ratio"]
    is_align = metadata["is_align"]
    is_marksheet = metadata["is_marksheet"]
    if is_marksheet:
        logger.info(f"is_marksheet == 1")
        metadata["sheet"] = read_mark_setting(metadata_path, resize_ratio)
        mark_reader = MarkReader(metadata)
        marksheet_result_path = os.path.join(save_dir, f"marksheet_result_{NOW}.csv")
        logger.info(f"Marksheet result is saved at {marksheet_result_path}")
        marksheet_result_header = ["origin_filename", "save_filename"] + list(
            metadata["sheet"].keys()
        )
        marksheet_result_writer = MarksheetResultWriter(
            marksheet_result_path, marksheet_result_header
        )
    else:
        logger.info(f"is_marksheet == 0")

    img_iter = read_images(img_dir, resize_ratio=resize_ratio)

    # read base image
    logger.debug(f"Begin reading the base image {baseimg_path}")
    baseimg, dpi = read_image(baseimg_path, resize_ratio=resize_ratio)
    if baseimg is None:
        logger.error(f"The file {baseimg_path} is not an image.")
        raise FileExistsError(f"The file {baseimg_path} is not an image.")
    if is_align:
        aligner = ImageAligner(metadata)
        aligner.fit(baseimg)

    # values = []
    error_paths = []
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
            v["origin_filename"] = filename
            # values.append(v)
        else:
            v = None
        # Set your customized filename
        save_filename = decide_save_filename(filename, v)
        save_filename = image_saver.save(save_filename, img, dpi)
        q = os.path.join(save_dir, save_filename)
        logger.info(f"{p} -> {q} saved.")
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


def read_args():
    """
    Read argument.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--console_log",
        type=int,
        choices=(10, 20, 30, 40, 50),
        default=logging.INFO,
        help="Set console log level.",
    )
    parser.add_argument(
        "-f",
        "--file_log",
        type=int,
        choices=(10, 20, 30, 40, 50),
        default=logging.WARN,
        help="Set file log level.",
    )
    args = parser.parse_args()

    while True:
        img_dir = input("対象となるフォルダ名を相対パスで指定してください。\n:")
        if img_dir:
            if os.path.isdir(img_dir):
                break
            else:
                print(f"フォルダ{img_dir}が存在しません。正しいパスを指定してください。")
        else:
            print("これは必須項目です。必ず指定してください。")

    metadata_path_default = "setting.xlsx"
    while True:
        metadata_path = input(
            f"設定ファイルを保存しているファイルを相対パスで指定してください。デフォルト:{metadata_path_default}\n:"
        )
        if not metadata_path:
            metadata_path = metadata_path_default
        if os.path.exists(metadata_path):
            break
        print(f"{metadata_path}が存在しません。正しいパスを指定してください。")

    save_dir_default = img_dir + "_processed"
    while True:
        save_dir = input(f"保存先のフォルダ名を相対パスで指定してください。デフォルト:{save_dir_default}\n:")
        if not save_dir:
            save_dir = save_dir_default
        if os.path.exists(save_dir):
            yn = input("既に存在するパスを指定しています。画像データは上書きされますが、よろしいですか？(y/n):")
            if yn == "y":
                break
        else:
            break

    baseimg_path_default = "baseimg.jpg"
    while True:
        baseimg_path = input(f"整列の際にベースとなる画像を選択してください。デフォルト:{baseimg_path_default}\n:")
        if not baseimg_path:
            baseimg_path = baseimg_path_default
        if os.path.exists(baseimg_path):
            break
        print(f"{baseimg_path}が存在しません。正しいパスを指定してください。")

    return args, img_dir, metadata_path, save_dir, baseimg_path


def main():
    args, img_dir, metadata_path, save_dir, baseimg_path = read_args()
    start = time.time()  # start time
    setup_logger(args.console_log, save_dir, args.file_log)
    try:
        pipeline(img_dir, metadata_path, save_dir, baseimg_path)
        end = time.time()  # end time
        exetime = end - start
        logger.info(f"ALL PROCESSES FINISHED.\n Time: {exetime} s.")
    except Exception as e:
        end = time.time()
        exetime = end - start
        logger.exception(f"STOPPED!!! Time: {exetime} s.")
        raise e


if __name__ == "__main__":
    main()
