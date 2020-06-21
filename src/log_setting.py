from logging import getLogger, StreamHandler, FileHandler
from typing import Union


def get_logger(
    console_mode: Union[str, int] = "warning",
    logpath: Union[str, None] = None,
    file_mode: Union[str, int] = "waring",
):

    logger = getLogger("stchger")
    logger.setLevel(console_mode)
    stream_handler = StreamHandler()
    stream_handler.setLevel(console_mode)
    logger.addHandler(stream_handler)
    if logpath:
        file_handler = FileHandler(logpath)
        file_handler.setLevel(file_mode)
        logger.addHandler(file_handler)

    return logger
