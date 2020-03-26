#!/usr/bin/env python

import cv2
import os
import glob


def read_images(dirname):
    """
    Parameters
    ----------
    dirname: name of the directory.
    """
    pathr = os.path.join(dirname, "**")
    paths = glob.iglob(pathr, recursive=True)
    for p in paths:
        img = cv2.imread(p)
        if img is None:
            continue
        yield p, img


def save_image(path, img):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)


def main():
    dirname = input(
        "対象のフォルダ名を相対パスで指定してください。\n例 ./data/raw\n: "
    )
    if not dirname:
        raise ValueError("対象のフォルダ名を指定してください。")
    dirname = dirname.rstrip("/").rstrip("\\")
    after_dirname = input(
        f"保存先のフォルダ名を先程と同じ形式で入力してください。\n例 ./data/processed（デフォルト {dirname}_resized)\n: "
    )
    if not after_dirname:
        after_dirname = dirname + "_resized"
    after_dirname = after_dirname.rstrip("/").rstrip("\\")
    rate = input("リサイズの比率を小数で入力してください。(デフォルト 0.5): ")
    if not rate:
        rate = 0.5
    else:
        rate = float(rate)

    for p, img in read_images(dirname):
        resized = cv2.resize(img, None, fx=rate, fy=rate, interpolation=cv2.INTER_AREA)
        q = p.replace(dirname, after_dirname)
        save_image(q, resized)


if __name__ == "__main__":
    main()
