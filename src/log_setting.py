import os
import logging
from logging import getLogger, StreamHandler, FileHandler, Formatter
from typing import Union

LOGLEVEL = logging.DEBUG


def set_logger(
    console_mode: int = LOGLEVEL,
    logpath: Union[str, None] = None,
    file_mode: int= LOGLEVEL,
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

    Returns
    -------
    logger
    """

    logger = getLogger("adjust-scan-images")
    logger.setLevel(console_mode)

    handler_format = Formatter(
        '%(asctime)s-%(levelname)s: %(message)s')

    stream_handler = StreamHandler()
    stream_handler.setLevel(console_mode)
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)

    if logpath:
        file_handler = FileHandler(logpath)
        file_handler.setLevel(file_mode)
        file_handler.setFormatter(handler_format)
        logger.addHandler(file_handler)
