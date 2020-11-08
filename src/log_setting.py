import os
import logging
from logging import getLogger, StreamHandler, FileHandler, Formatter
from typing import Optional

from .const import NOW

logger = getLogger("adjust-scan-images")


def set_logger(
    console_mode: int = logging.INFO,
    logpath: Optional[str] = None,
    file_mode: int = logging.WARN,
):
    """
    Get logger.

    Parameters
    ----------
    console_mode : int, optional
        log level, by default 20
    logpath : Union[str, None], optional
        save file path, by default None
    file_mode : int, optional
        log level, by default 20
    """

    logger.setLevel(console_mode)

    handler_format = Formatter("%(asctime)s-%(levelname)s: %(message)s")

    stream_handler = StreamHandler()
    stream_handler.setLevel(console_mode)
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)

    if logpath:
        file_handler = FileHandler(logpath)
        file_handler.setLevel(file_mode)
        file_handler.setFormatter(handler_format)
        logger.addHandler(file_handler)


def setup_logger(console_mode: int, save_dir: str, file_mode: int):
    """
    Set up log.

    Parameters
    ----------
    console_mode : int
        Console log level.
    save_dir : str
        The directory where the logs are saved.
    file_mode : int
        File log level.
    """
    # log setting
    os.makedirs(save_dir, exist_ok=True)
    logpath = os.path.join(save_dir, f"log_{NOW}.txt")
    set_logger(console_mode, logpath, file_mode)
    logger.info(f"Log saving at {logpath}.")
