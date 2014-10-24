# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import io
import json
import os
import click

from . import BaseAdapter
from .config_parser import ConfigParser

from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

from pprint import pprint as pp

class VcfAdapter(BaseAdapter):
  """docstring for API"""
  
  def init_app(self, app, vcf_directory=None, config_file=None):
    # get root path of the Flask app
    # project_root = '/'.join(app.root_path.split('/')[0:-1])
    
    # combine path to the local development fixtures
    project_root = '/vagrant/scout'
    cases_path = os.path.join(project_root,vcf_directory)
    
    self.config_object = ConfigParser(config_file)
    
    self._cases = []
    self._variants = {} # Dict like {case_id: variant_parser}
    
    self.get_cases(cases_path) 
    
    for case in self._cases:
      self._variants[case['id']] = vcf_parser.VCFParser(infile = case['vcf_path'])


  def get_cases(self, cases_path):
    """Take a case file and return the case on the specified format."""
    
    ########### Loop over the case folders. Structure is described in documentation ###########
    
    for root, dirs, files in os.walk(cases_path):
      if files:
        ped_file = None
        vcf_file = None
        zipped_vcf_file = None
        case = None
        for file in files:
          if os.path.splitext(file)[-1] == '.ped':
            ped_file = os.path.join(root, file)
            case_parser = ped_parser.FamilyParser(ped_file)
            case = case_parser.get_json()[0]
          if os.path.splitext(file)[-1] == '.vcf':
            vcf_file = os.path.join(root, file)
          if os.path.splitext(file)[-1] == '.gz':
            if os.path.splitext(file)[0][-1] == '.gz':
              zipped_vcf_file = os.path.join(root, file)
        # If no vcf we search for zipped files
        if not vcf_file:
          vcf_file = zipped_vcf_file
        # If ped and vcf are not found exit:
        if not (ped_file and vcf_file):
          raise SyntaxError('Wrong folder structure in vcf directories. '
                            'Could not find ped and/or vcf files. '
                              'See documentation.')
        # Store the path to variants as case id:s:
        case['id'] = case['family_id']
        case['vcf_path'] = vcf_file
        self._cases.append(case)
    
    return
  
  
  def cases(self):
    return self._cases

  def case(self, case_id):
    for case in self._cases:
      if case['id'] == case_id:
        return case
  
  
  def format_variant(self, variant):
    """Return the variant in a format specified for scout."""
    
    def get_value(variant, category, member):
      """Return the correct value from the variant according to rules in config parser.
          vcf_fiels can be one of the following[CHROM, POS, ID, REF, ALT, QUAL, INFO, FORMAT, individual, other]"""
      # If information is on the core we can access it directly through the vcf key
      value = None
      # In this case we read straight from the vcf line
      if self.config_object[member]['vcf_field'] not in ['INFO', 'FORMAT', 'other', 'individual']:
        value = variant[self.config_object[member]['vcf_field']]
      
      # In this case we need to check the info dictionary:
      elif self.config_object[member]['vcf_field'] == 'INFO':
        value = variant['info_dict'].get(self.config_object[member]['vcf_info_key'], None)
      
      # Check if we should return a list:
      if value and self.config_object[member]['vcf_data_field_number'] != '1':
        value = value.split(self.config_object[member]['vcf_data_field_separator'])
      return value
      
    formated_variant = {}
    formated_variant['id'] = variant['variant_id']
    for category in self.config_object.categories:
      for member in self.config_object.categories[category]:
        if category != 'config_info':
          formated_variant[self.config_object[member]['internal_record_key']] = get_value(variant, category, member)
    
    return formated_variant
  
  
  def variants(self, case, query=None, variant_ids=None, nr_of_variants = 100):
  
    # if variant_ids:
    #   return self._many_variants(variant_ids)

    variants = []
    i = 0
    for variant in self._variants[case]:
      if i < nr_of_variants:
        yield self.format_variant(variant)
        i += 1
      else:
        return

  def _many_variants(self, variant_ids):
    variants = []

    for variant in self._variants:
      if variant['id'] in variant_ids:
        variants.append(variant)

    return variants

  def variant(self, variant_id):
    for variant in self._variants:
      if variant['id'] == int(variant_id):
        return variant

    return None

  def create_variant(self, variant):
    # Find out last ID
    try:
      last_id = self._variants[-1]['id']
    except IndexError:
      last_id = 0

    next_id = last_id + 1

    # Assign id to the new variant
    variant['id'] = next_id

    # Add new variant to the list
    self._variants.append(variant)

    return variant

@click.command()
@click.argument('vcf_dir',
                nargs=1,
                type=click.Path(exists=True)
)
# @click.argument('ped_file',
#                 nargs=1,
#                 type=click.Path(exists=True)
# )
@click.argument('config_file',
                nargs=1,
                type=click.Path(exists=True)
)
# @click.argument('outfile',
#                 nargs=1,
#                 type=click.File('w')
# )
def cli(vcf_dir, config_file):
    """Test the vcf class."""
    my_vcf = VcfAdapter()
    my_vcf.init_app('app', vcf_dir, config_file)
    
    print(my_vcf.cases())
    print('')
    
    for case in my_vcf._cases:
      for variant in my_vcf.variants(case['id']):
        pp(variant)
    #   print('')

if __name__ == '__main__':
    cli()
