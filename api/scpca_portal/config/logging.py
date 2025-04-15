import logging
import os
import sys
import time
from datetime import datetime
from functools import wraps
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
LOG_RUNTIMES = os.getenv("LOG_RUNTIMES", False)


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


def get_formatted_time(timestamp: float) -> str:
    """Return string representation of a timestamp in Hour:Minute:Second:Millisecond format."""
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S.%f")[:-3]  # remove microseconds


def log_runtime(logger):
    """Log the start time, end time, and duration of the wrapped function."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global LOG_RUNTIMES  # noqa: F824
            if not LOG_RUNTIMES:
                return func(*args, **kwargs)

            func_name = f"{func.__module__}::{func.__name__}"
            start_time = time.time()
            logger.info(f"\nEntering function '{func_name}'.")

            try:
                result = func(*args, **kwargs)
            finally:
                end_time = time.time()
                duration = end_time - start_time
                logger.info(
                    f"\nExited function '{func_name}'.\n"
                    f"Function run time: {get_formatted_time(duration)} "
                    f"(Start: {get_formatted_time(start_time)}, "
                    f"End: {get_formatted_time(end_time)})"
                )

            return result

        return wrapper

    return decorator


def configure_runtime_logging(logger: logging.Logger):
    """Return log_runtime decorator pre-configured to a specific logger."""
    return log_runtime(logger)
