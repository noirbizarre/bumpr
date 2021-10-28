from __future__ import annotations

import logging
import os
import sys
from logging import DEBUG, INFO, Formatter, StreamHandler
from typing import cast

__all__ = ("init",)

RESET_TERM = "\033[0;m"

COLOR_CODES = {
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "bgred": 41,
    "bggrey": 100,
}

LEVEL_COLORS = {
    "DEBUG": "blue",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bgred",
}

DRYRUN = 25
DIFF = 15


def ansi(color, text):
    """Wrap text in an ansi escape sequence"""
    code = COLOR_CODES[color]
    return "\033[1;{0}m{1}{2}".format(code, text, RESET_TERM)


class ANSIFormatter(Formatter):
    """
    Convert a `logging.LogRecord' object into colored text, using ANSI
    escape sequences.
    """

    def format(self, record):
        msg = record.getMessage()
        if record.levelname == "INFO":
            return ansi("cyan", "-> ") + msg
        elif record.levelname == "DRYRUN":
            return ansi("magenta", "dryrun-> ") + msg
        elif record.levelname == "DIFF":
            if msg.startswith("+"):
                return ansi("green", msg)
            elif msg.startswith("-"):
                return ansi("red", msg)
            else:
                return msg
        else:
            color = LEVEL_COLORS.get(record.levelname, "white")
            return ansi(color, record.levelname.lower()) + ": " + msg


class TextFormatter(Formatter):
    """
    Convert a `logging.LogRecord' object into text.
    """

    def format(self, record):
        if not record.levelname or record.levelname in ("INFO", "DIFF"):
            return record.getMessage()
        elif record.levelname == "DRYRUN":
            return "dryrun-> {0}".format(record.getMessage())
        else:
            return record.levelname.lower() + ": " + record.getMessage()


class BumprLogger(logging.Logger):
    def dryrun(self, *args):
        self.log(DRYRUN, *args)

    def diff(self, *args):
        self.log(DIFF, *args)


def declare():
    logging.addLevelName(DRYRUN, "DRYRUN")
    logging.addLevelName(DIFF, "DIFF")
    logging.setLoggerClass(BumprLogger)


def init(level=INFO):
    declare()

    logger = logging.getLogger()
    handler = StreamHandler()

    if os.isatty(sys.stdout.fileno()) and not sys.platform.startswith("win"):
        fmt = ANSIFormatter()
    else:
        fmt = TextFormatter()
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    if level:
        logger.setLevel(level)


if __name__ == "__main__":  # pragma: no cover
    init(level=DEBUG)

    logger = cast(BumprLogger, logging.getLogger(__name__))
    logger.debug("debug")
    logger.dryrun("dryrun")
    logger.diff("diff")
    logger.diff("+ diff")
    logger.diff("- diff")
    logger.info("info")
    logger.warning("warning")
    logger.error("error")
    logger.critical("critical")
