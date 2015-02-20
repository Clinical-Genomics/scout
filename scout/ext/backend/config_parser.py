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

from configobj import ConfigObj, flatten_errors
from validate import Validator

from ped_parser import parser as ped_parser
from vcf_parser import parser as vcf_parser

from pprint import pprint as pp


class ConfigParser(ConfigObj):
  """Class for holding information from config file"""
  def __init__(self, config_file, indent_type='  ', encoding='utf-8', configspec=None):
    if configspec:
      super(ConfigParser, self).__init__(
                                          infile=config_file, 
                                          indent_type=indent_type, 
                                          encoding=encoding,
                                          configspec=configspec
                                      )
      validator = Validator()
      results = self.validate(validator)
      if results != True:
        for (section_list, key, _) in flatten_errors(self, results):
            if key is not None:
              print('The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
            else:
              print('The following section was missing:%s ' % ', '.join(section_list))
          # print('Config file validation failed!')
          # sys.exit(1)
      
    else:
      super(ConfigParser, self).__init__(
                                          infile=config_file, 
                                          indent_type=indent_type, 
                                          encoding=encoding,
                                          configspec=configspec
                                      )
    
    self.categories = {
                  'variant_position':[],
                  'variant_id':[],
                  'variant_information':[],
                  'allele_frequency':[],
                  'conservation': [],
                  'deleteriousness':[],
                  'inheritance_models':[],
                  'config_info':[],
                  'gene_identifier':[],
                  'genotype_information':[]
                }

    self.plugins = [plugin for plugin in self.get('VCF', {}).keys()]
    if self.plugins:
      for plugin in self.plugins:
        self.categories[self['VCF'][plugin]['category']].append(plugin)
    
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
@click.option('-s', '--config_spec',
                nargs=1,
                type=click.Path()
)
@click.option('-out', '--outfile',
                nargs=1,
                type=click.File('w')
)
def read_config(config_file, config_spec, outfile):
    """Parse the config file and print it to the output."""
    my_config_reader = ConfigParser(config_file, configspec=config_spec)
    print('\nCategories:\n' '-------------------')
    # pp(my_config_reader)
    for category in my_config_reader.categories:
      print(category)
      for category_name in my_config_reader.categories[category]:
        print('\t %s' %category_name)
      # for adapter in my_config_reader.categories[category]:
      #   print('%s : %s' % (category, adapter))
      #   pp(dict(my_config_reader['VCF'][adapter]))
        # print(type(my_config_reader['VCF'][adapter]))
    # for plugin in my_config_reader.plugins:
    #   print(type(my_config_reader[plugin].get('vcf_data_field_number', '0')))
      
    # if outfile:
    #     my_config_reader.write_config(outfile)
    
    
if __name__ == '__main__':
    read_config()