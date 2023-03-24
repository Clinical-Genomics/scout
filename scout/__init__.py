# -*- coding: utf-8 -*-
try:
    from importlib.metadata import version
except ImportError:  # Backport support for importlib metadata on Python 3.7
    from importlib_metadata import version

__version__ = version("scout-browser")
