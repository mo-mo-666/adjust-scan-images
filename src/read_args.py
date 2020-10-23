import argparse
import sys
import os
import glob
import logging


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
        metadata_path = input(f"設定ファイルを相対パスで指定してください。デフォルト:{metadata_path_default}\n:")
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

    baseimg_path_default = "対象フォルダのうち，辞書順でもっとも最初の画像"
    img_ext = (
        ".jpg",
        ".JPG",
        ".jpeg",
        ".JPEG",
        ".png",
        ".PNG",
        ".bmp",
        ".gif",
        ".tif",
        ".tiff",
    )
    while True:
        baseimg_path = input(
            f"位置合わせの基準となる画像のパスを指定してください。位置合わせを行わない場合，単にエンターを押してください。デフォルト:{baseimg_path_default}\n:"
        )
        if not baseimg_path:
            baseimg_paths = glob.glob(os.path.join(img_dir, "*"))
            baseimg_paths = tuple(
                sorted(
                    [p for p in baseimg_paths if os.path.splitext(p)[1] in img_ext],
                    key=lambda x: os.path.splitext(x)[0],
                )
            )
            if not baseimg_paths:
                print(f"{img_dir}に画像{img_ext}が存在しないため，処理を終了します。")
                sys.exit()
            baseimg_path = baseimg_paths[0]
            break
        if not os.path.splitext(baseimg_path)[-1] in img_ext:
            print(f"{baseimg_path}は画像ではありません。画像は拡張子{img_ext}まで指定してください。")
            continue
        if not os.path.exists(baseimg_path):
            print(f"{baseimg_path}が存在しません。正しいパスを指定してください。")
            continue
        break

    return args, img_dir, metadata_path, save_dir, baseimg_path
