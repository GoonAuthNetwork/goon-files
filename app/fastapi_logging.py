import logging
import sys
from pathlib import Path
from loguru import logger
from .config import LOGGING_CONFIG

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


class CustomizeLogger:
    @classmethod
    def make_logger(cls):
        """
        file = Path.joinpath(
            LOGGING_CONFIG["file"]["path"], LOGGING_CONFIG["file"]["name"]
        )
        """
        file = None

        logger = cls.customize_logging(
            file,
            LOGGING_CONFIG["level"],
            retention=LOGGING_CONFIG["file"]["retention"],
            rotation=LOGGING_CONFIG["file"]["rotation"],
            format=LOGGING_CONFIG["format"],
        )

        return logger

    @classmethod
    def customize_logging(
        cls, filepath: Path, level: str, rotation: str, retention: str, format: str
    ):

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
