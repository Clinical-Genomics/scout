#!/usr/bin/env python
# encoding: utf-8
"""
read_config.py

Some tests reading the config file

Created by Måns Magnusson on 2014-10-19.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import click

from configobj import ConfigObj

from ped_parser import parser as ped_parser
from vcf_parser import parser as vcf_parser

from pprint import pprint as pp

def index(directory):
    # like os.listdir, but traverses directory trees
    stack = [directory]
    files = []
    while stack:
        directory = stack.pop()
        for file in os.listdir(directory):
            fullname = os.path.join(directory, file)
            files.append(fullname)
            if os.path.isdir(fullname) and not os.path.islink(fullname):
                stack.append(fullname)
    return files


@click.command()
# @click.argument('vcf_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
# @click.argument('ped_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
@click.argument('config_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.argument('outfile',
                nargs=1,
                type=click.File('w')
)
def read_config(config_file, outfile):
    """Parse the config file and print it to the output."""
    cfg = ConfigObj(infile=config_file, indent_type='    ', encoding='utf-8')
    cfg.write(outfile)
    
    
if __name__ == '__main__':
    read_config()