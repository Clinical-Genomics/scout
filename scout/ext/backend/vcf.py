# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import io
import json
import os
import click

from .base import BaseAdapter
from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser

class VcfAdapter(BaseAdapter):
  """docstring for API"""
  
  def init_app(self, app):
    # get root path of the Flask app
    # project_root = '/'.join(app.root_path.split('/')[0:-1])
    project_root = '/vagrant/scout'
    self._families = []
    self._variants = {} # Dict like {family_id: variant_parser}
    ################################### TEMPORARY SOLUTION #######################################
    # We should loop over the files in the vcf directory later
    family_1_path = os.path.join(project_root, 'tests/vcf_examples/1/1.ped')
    family_2_path = os.path.join(project_root, 'tests/vcf_examples/2/2.ped')
    
    variants_1_path = os.path.join(project_root, 'tests/vcf_examples/1/test_vcf.vcf')
    variants_2_path = os.path.join(project_root, 'tests/vcf_examples/2/test_vcf.vcf')
    
    ##############################################################################################
    families_path = os.path.join(project_root, 'tests/vcf_examples')
    for root, dirs, files in os.walk(families_path):
        for file in files:
          print('root: %s, dirs: %s , files: %s , file: %s' % (str(root), str(dirs), str(files), str(file)))
          print(os.path.splitext(file))
          if os.path.splitext(file)[-1] == '.ped':
            print('PED file! %s' % file)
          if os.path.splitext(file)[-1] == '.vcf':
              print('VCF file! %s' % file)
          if os.path.splitext(file)[-1] == '.gz':
            if os.path.splitext(file)[0][-1] == '.gz':
              print('Zipped VCF file! %s' % file)
    
    self._families.append(self.get_family(family_1_path))
    self._families.append(self.get_family(family_2_path))
    
    self._variants['1'] = vcf_parser.VCFParser(infile = variants_1_path) 
    self._variants['2'] = vcf_parser.VCFParser(infile = variants_2_path) 
    
    
  def get_family(self, family_file):
    """Take a family file and return the family on the specified format."""
    family_parser = ped_parser.FamilyParser(family_file)
    return family_parser.get_json()[0]
    
  
  def families(self):
    return self._families

  def family(self, family_id):
    for family in self._families:
      if family['id'] == family_id:
        return family
    
    return None
  
  def variants(self, family, query=None, variant_ids=None, nr_of_variants = 100):
    
    # if variant_ids:
    #   return self._many_variants(variant_ids)
    def format_variant(variant):
      """Return the variant in a format specified for scout."""
      return variant
    
    variants = []
    i = 0
    for variant in self._variants[family]:
      if i < nr_of_variants:
        yield format_variant(variant)
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
# @click.argument('outfile',
#                 nargs=1,
#                 type=click.File('w')
# )
def cli():
    """Test the vcf class."""
    my_vcf = VcfAdapter()
    my_vcf.init_app('app')
    print(my_vcf._families)
    for variant in my_vcf.variants('1'):
      print(variant)
    
if __name__ == '__main__':
    cli()