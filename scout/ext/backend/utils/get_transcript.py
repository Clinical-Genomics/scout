#!/usr/bin/env python
# encoding: utf-8
"""
get_transcript.py

Parse all information for genes and build mongo engine objects.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""
import click

from scout.models import Transcript
from .constants import SO_TERMS



