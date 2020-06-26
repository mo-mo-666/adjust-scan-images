import os
import csv
import datetime
import cv2
import logging
from typing import Tuple, Union

from .setting_io import read_metadata, read_mark_setting
from .image_io import read_image, read_images
from .align_images import ImageAligner
from .read_marksheet import MarkReader
from .log_setting import get_logger
from .errors import MarkerNotFoundError


def save_filepath(save_dir: str, read_filename: str, value: Union[dict, None] = None):
    save_filename = read_filename
    if value:
        pass
    return os.path.join(save_dir, save_filename)


def save_marksheetdata(data, path):
    pass


def pipeline(img_dir: str, metadata_path: str, save_dir: str, baseimg_path: str):

    # log setting
    os.makedirs(save_dir, exist_ok=True)
    now = datetime.datetime.now()
    now = f"{now.year}{now.month:02}{now.day:02}{now.hour:02}{now.minute:02}{now.second:02}"
    logpath = os.path.join(save_dir, f"log_{now}.txt")
    logger = get_logger(logpath=logpath)

    # log for parameters
    logger.info(f"Log saving at {logpath}.")
    logger.info(f"img_dir: {img_dir}")
    logger.info(f"metadata_path: {metadata_path}")
    logger.info(f"save_dir: {save_dir}")
    logger.info(f"baseimg_path: {baseimg_path}")

    # read metadata
    try:
        metadata = read_metadata(metadata_path)

        resize_ratio = metadata["resize_ratio"]
        is_align = metadata["is_align"]
        is_markread = metadata["is_markread"]
        if is_markread:
            logger.info(f"is_markread == 1")
            metadata["sheet"] = read_mark_setting(metadata_path, resize_ratio)
            mark_reader = MarkReader(metadata)
        else:
            logger.info(f"is_markread == 0")
    except Exception as err:
        logger.error(err)
        raise err

    img_iter = read_images(img_dir, resize_ratio=resize_ratio)

    # read base image
    logger.debug(f"Begin reading the base image {baseimg_path}")
    baseimg = read_image(baseimg_path)
    if baseimg is None:
        logger.error(f"The file {baseimg_path} is not image.")
        raise FileNotFoundError(f"The file {baseimg_path} is not image.")
    if is_align:
        aligner = ImageAligner(metadata)
        aligner.fit(baseimg)

    values = []
    for p, img in img_iter:
        logger.debug(f"Begin processing for {p}")
        filename = os.path.basename(p)
        if is_align:
            try:
                img = aligner.transform_one(img)
            except MarkerNotFoundError:
                logger.error(f"The image '{p}' cannot be aligned since we cannot find markers.")
                continue
        if is_markread:
            v = mark_reader.read(img)
            v["filename"] = filename
            values.append(v)
        else:
            v = None
        # Set your customized filename
        q = save_filepath(save_dir, filename, v)
        cv2.imwrite(q, img)
        logger.info(f"{p} -> {os.path.join(save_dir, q)} saved.")

    return values


def read_args():

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
        metadata_path = input(f"設定ファイルを保存しているファイルを相対パスで指定してください。デフォルト:{metadata_path_default}\n:")
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
            yn = input("既に存在するパスを指定しています。データは上書きされますが、よろしいですか？(y/n):")
            if yn == "y":
                    break

    baseimg_path_default = "baseimg.jpg"
    while True:
        baseimg_path = input(f"整列の際にベースとなる画像を選択してください。")
        if not baseimg_path:
            baseimg_path = baseimg_path_default
        if os.path.exists(baseimg_path):
            break
        print(f"{metadata_path}が存在しません。正しいパスを指定してください。")

    return img_dir, metadata_path, save_dir, baseimg_path



def main():
    img_dir, metadata_path, save_dir, baseimg_path = read_args()
    pipeline(img_dir, metadata_path, save_dir, baseimg_path)


if __name__ == "__main__":
    main()
