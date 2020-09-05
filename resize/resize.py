import PIL
from PIL import Image
import os
import glob
import tqdm


def read_images(dirname, rate=1):
    """
    Parameters
    ----------
    dirname: name of the directory.
    """
    pathr = os.path.join(dirname, "**")
    paths = glob.glob(pathr, recursive=True)
    paths = [p for p in paths if os.path.isfile(p)]
    for p in tqdm.tqdm(paths):
        try:
            img = Image.open(p)
        except PIL.UnidentifiedImageError:
            continue
        dpi = img.info["dpi"]
        resized = img.resize((int(img.width * rate), int(img.height * rate)))
        dpi_resized = (int(dpi[0] * rate), int(dpi[1] * rate))
        yield p, resized, dpi_resized


def save_image(path, img, dpi):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, dpi=dpi)


def main():
    while True:
        dirname = input("対象のフォルダ名を相対パスで指定してください。\n例 ./data/raw\n: ")
        if dirname:
            break
        print("対象のフォルダ名は必ず指定してください。")
    dirname = dirname.rstrip("/").rstrip("\\")
    after_dirname = input(
        f"保存先のフォルダ名を先程と同じ形式で入力してください。\n例 ./data/processed（省略可。デフォルト {dirname}_resized)\n: "
    )
    if not after_dirname:
        after_dirname = dirname + "_resized"
    after_dirname = after_dirname.rstrip("/").rstrip("\\")
    while True:
        rate = input("リサイズの比率を小数で入力してください。(省略可。デフォルト 0.5): ")
        if not rate:
            rate = 0.5
            break
        else:
            try:
                rate = float(rate)
                break
            except:
                print("比率は小数で入力してください。")

    for p, img, dpi in read_images(dirname, rate):
        q = p.replace(dirname, after_dirname)
        save_image(q, img, dpi)


if __name__ == "__main__":
    main()
