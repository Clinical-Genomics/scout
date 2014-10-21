#!/usr/bin/env python
# encoding: utf-8
"""
load_mongo.py

Load a mongo db with information from vcf file.

Created by Måns Magnusson on 2014-10-17.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.
"""

from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import click

from ped_parser import parser as ped_parser
from vcf_parser import parser as vcf_parser


@click.command()
@click.argument('vcf_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.argument('ped_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.argument('config_file',
                nargs=1,
                type=click.Path(exists=True)
)
def load_mongo(vcf_file, ped_file, config_file):
    """Parse the files and add fill the mongo db."""
    vcf = vcf_parser(vcf_file)
    ped = ped_parser(ped_file)
    

if __name__ == '__main__':
    load_mongo()