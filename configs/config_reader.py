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

class ConfigParser(object):
  """Class for holding information from config file"""
  def __init__(self, config_file):
    super(ConfigParser, self).__init__()
    self._cfg = ConfigObj(infile=config_file, indent_type='    ', encoding='utf-8')
    self.collections = {'core':[], 
                    'common':[], 
                    'case':[], 
                    'config_info':[], 
                }
    self.categories = {'variant_position':[], 
                    'variant_id':[], 
                    'variant_information':[],
                    'allele_frequency':[],
                    'deleteriousness':[],
                    'inheritance_models':[],
                    'config_info':[], 
                    'gene_identifier':[]
                }
    
    self.plugins = [plugin for plugin in self._cfg.keys()]
    for plugin in self.plugins:
        self.collections[self._cfg[plugin]['collection']].append(plugin)
        self.categories[self._cfg[plugin]['category']].append(plugin)
    
  def write_config(self, outfile):
    """Write the config file to a new file"""
    self._cfg.write(outfile)

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
@click.option('-out', '--outfile',
                nargs=1,
                type=click.File('w')
)
def read_config(config_file, outfile):
    """Parse the config file and print it to the output."""
    my_config_reader = ConfigParser(config_file)
    pp(my_config_reader.collections)
    pp(my_config_reader.categories)
    if outfile:
        my_config_reader.write_config(outfile)
    
    
if __name__ == '__main__':
    read_config()