import logging
import os
import sys
from multiprocessing import current_process

import daiquiri


def get_thread_id() -> str:
    """Returns thread_id."""
    return current_process().name


# Most of the formatting in this string is for the logging system. All
# that the call to format() does is replace the "{0}" in the string
# with the thread id.
FORMAT_STRING = (
    "%(asctime)s {0} %(name)s %(color)s%(levelname)s%(extras)s" ": %(message)s%(color_stop)s"
).format(get_thread_id())
LOG_LEVEL = None


def unconfigure_root_logger():
    """Prevents the root logger from duplicating our messages.

    The root handler comes preconfigured with a handler. This causes
    all our logs to be logged twice, once with our cool handler and
    one that lacks all context. This function removes that stupid
    extra handler.
    """
    root_logger = logging.getLogger(None)
    # Remove all handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)


def get_and_configure_logger(name: str) -> logging.Logger:
    unconfigure_root_logger()

    global LOG_LEVEL
    if LOG_LEVEL is None:
        LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    logger = daiquiri.getLogger(name)
    logger.setLevel(logging.getLevelName(LOG_LEVEL))

    # This is the local handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(daiquiri.formatter.ColorExtrasFormatter(fmt=FORMAT_STRING, keywords=[]))
    logger.logger.addHandler(handler)

    return logger
