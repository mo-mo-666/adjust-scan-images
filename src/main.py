import time
import logging

from .pipeline import pipeline
from .read_args import read_args
from .log_setting import setup_logger

logger = logging.getLogger("adjust-scan-images")


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
