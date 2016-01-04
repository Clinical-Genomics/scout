# -*- coding: utf-8 -*-
import os
import logging
import scout
from pkg_resources import get_distribution

__version__ = get_distribution('scout-browser').version
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(scout.__file__), '..'))
logger = logging.getLogger()
