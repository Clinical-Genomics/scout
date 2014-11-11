#!/usr/bin/env python
# encoding: utf-8
"""
test_vcf.py

Some tests for writing the vcf adapter

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
# @click.argument('config_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
def test_vcf():
    """Parse the files and add fill the mongo db."""
    families_path = '/vagrant/scout/tests/vcf_examples'
    families = {}
    # print(families_path)
    # print(os.path.exists(families_path))
    # for file in index(families_path):
    #     print(file)
    i = 0
    for root, dirs, files in os.walk(families_path):
        print('root: %s, dirs: %s , files: %s' % (str(root), str(dirs), str(files)))
        for f in files:
            print('File: %s' % f)
            if os.path.splitext(f)[-1] == '.ped':
                if i in families:
                    families[i]['ped'] = os.path.join(root, f)
                else:
                    families[i] = {'ped' : os.path.join(root, f)}
            if os.path.splitext(f)[-1] == '.vcf':
                if i in families:
                    families[i]['vcf'] = os.path.join(root, f)
                else:
                    families[i] = {'vcf' : os.path.join(root, f)}
        i += 1
    for i in families:
        my_family = ped_parser.FamilyParser(families[i]['ped'])
        print(my_family.make_json(), type(my_family.make_json()))
    pp(families)
                

if __name__ == '__main__':
    test_vcf()