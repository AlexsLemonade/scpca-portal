# NOTE: To prevent circular import errors, this file can not be imported via /__init__.py
# Replacement of distutils.utils.strtobool:
# https://github.com/python/cpython/blob/e1a8a0393cd0869b72b6be559a2b145f1ff8c169/Lib/distutils/util.py#L308C1-L321C60
def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))
