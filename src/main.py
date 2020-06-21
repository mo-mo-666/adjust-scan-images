import os
import csv
from typing import Tuple, Union

from .setting_io import read_metadata, read_mark_setting
from .image_io import read_image, read_images, save_image
from .align_images import ImageAligner
from .read_marksheet import MarkReader
from .log_setting import get_logger


def save_filepath(save_dir: str, read_filename: str, value: Union[dict, None] = None):
    save_filename = read_filename
    if value:
        pass
    return os.path.join(save_dir, save_filename)


def save_marksheetdata(data, path):
    pass


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
    logger = get_logger()
    pipeline(img_dir, metadata_path, save_dir, baseimg_path)


if __name__ == "__main__":
    main()
