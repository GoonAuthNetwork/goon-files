import logging
import sys
from pathlib import Path
from loguru import logger
from app.config import LOGGING_CONFIG

"""
This file essentually taken from:
https://medium.com/1mgofficial/how-to-override-uvicorn-logger-in-fastapi-using-loguru-124133cdcd4e
"""


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def customize_logging():

    """
    filepath: Path = Path.joinpath(
        LOGGING_CONFIG["file"]["path"], LOGGING_CONFIG["file"]["name"]
    )
    """

    filepath: Path = None
    level: str = LOGGING_CONFIG["level"]
    rotation: str = LOGGING_CONFIG["file"]["rotation"]
    retention: str = LOGGING_CONFIG["file"]["retention"]
    format: str = LOGGING_CONFIG["format"]

    logger.remove()
    logger.add(
        sys.stdout, enqueue=True, backtrace=True, level=level.upper(), format=format
    )
    if filepath is not None:
        logger.add(
            str(filepath),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        _logger = logging.getLogger(_log)
        _logger.propagate = False
        _logger.handlers = [InterceptHandler()]

    return logger.bind(request_id=None, method=None)
