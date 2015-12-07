#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scout.__main__
~~~~~~~~~~~~~~~~~~~~~

The main entry point for the command line interface.

Invoke as ``scout`` (if installed)
or ``python -m scout`` (no install required).
"""
import sys

from scout.commands import cli


if __name__ == '__main__':
    # exit using whatever exit code the CLI returned
    sys.exit(cli())
