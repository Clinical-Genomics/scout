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
from validate import Validator

from ped_parser import parser as ped_parser
from vcf_parser import parser as vcf_parser

from pprint import pprint as pp

#Validation scheme for scout config files
SPEC = """
collection = option('core','common','case', 'config_info', 'specific')
categories = option('variant_position','variant_id','variant_information',allele_frequency','deleteriousness','inheritance_models','config_info','gene_identifier')
vcf_field = option('CHROM', 'CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL','INFO', 'FORMAT', 'other', default='other')
internal_record_key = string
scout_record_alias = string
vcf_data_field_type = option('string', 'int', 'float', 'list', default='string')
vcf_data_field_number = int
vcf_data_field_description = string
vcf_data_field_separator = string
""".split('\n')

# canvas_border = integer(min=10, max=35, default=15)
# colour1 = list(min=3, max=3, default=list('280', '0', '0'))
# colour2 = list(min=3, max=3, default=list('255', '255', '0'))
# colour3 = list(min=3, max=3, default=list('0', '255', '0'))
# colour4 = list(min=3, max=3, default=list('255', '0', '0'))
# colour5 = list(min=3, max=3, default=list('0', '0', '255'))
# colour6 = list(min=3, max=3, default=list('160', '32', '240'))
# colour7 = list(min=3, max=3, default=list('0', '255', '255'))
# colour8 = list(min=3, max=3, default=list('255', '165', '0'))
# colour9 = list(min=3, max=3, default=list('211', '211', '211'))
# convert_quality = option('highest', 'high', 'normal', default='normal')
# default_font = string
# default_width = integer(min=1, max=12000, default=640)
# default_height = integer(min=1, max=12000, default=480)
# imagemagick_path = string
# handle_size = integer(min=3, max=15, default=6)
# language = option('English', 'English (United Kingdom)', 'Russian', 'Hindi', default='English')
# print_title = boolean(default=True)
# statusbar = boolean(default=True)
# toolbar = boolean(default=True)
# toolbox = option('icon', 'text', default='icon')
# undo_sheets = integer(min=5, max=50, default=10)




class ConfigParser(ConfigObj):
  """Class for holding information from config file"""
  def __init__(self, config_file, indent_type='  ', encoding='utf-8'):
    super(ConfigParser, self).__init__(infile=config_file, indent_type=indent_type, encoding=encoding)
    # validator = Validator()
    # result = self.validate(validator)
    # if result != True:
    #     print('Config file validation failed!')
    #     sys.exit(1)
    self.collections = {'core':[],
                        'common':[],
                        'case':[],
                        'config_info':[],
                        'individual':[]
                }
    self.categories = {'variant_position':[],
                      'variant_id':[],
                      'variant_information':[],
                      'allele_frequency':[],
                      'deleteriousness':[],
                      'inheritance_models':[],
                      'config_info':[],
                      'gene_identifier':[],
                      'genotype_information':[]
                }

    self.plugins = [plugin for plugin in self.keys()]
    for plugin in self.plugins:
      self.collections[self[plugin]['collection']].append(plugin)
      self.categories[self[plugin]['category']].append(plugin)
    
  def write_config(self, outfile):
    """Write the config file to a new file"""
    self._cfg.write(outfile)



########### Command Line Interface for the config parser: #############
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
    print('Collections:\n' '-------------------')
    for collection in my_config_reader.collections:
      for adapter in my_config_reader.collections[collection]:
        print('%s : %s' % (collection, adapter))
    print('\nCategories:\n' '-------------------')
    for category in my_config_reader.categories:
      for adapter in my_config_reader.categories[category]:
        print('%s : %s' % (category, adapter))
    # for plugin in my_config_reader.plugins:
    #   print(type(my_config_reader[plugin].get('vcf_data_field_number', '0')))
      
    # if outfile:
    #     my_config_reader.write_config(outfile)
    
    
if __name__ == '__main__':
    read_config()