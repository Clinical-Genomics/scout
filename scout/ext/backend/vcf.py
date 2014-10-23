# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import io
import json
import os
import click

from . import BaseAdapter
from vcf_parser import parser as vcf_parser
from ped_parser import parser as ped_parser


class VcfAdapter(BaseAdapter):
  """docstring for API"""
  # , app
  # init_app
  def __init__(self, app=None):
    # get root path of the Flask app
    # project_root = '/'.join(app.root_path.split('/')[0:-1])
    
    # combine path to the local development fixtures
    project_root = '/vagrant/scout'
    cases_path = os.path.join(project_root, 'tests/vcf_examples')
    
    self._cases = []
    self._variants = {} # Dict like {case_id: variant_parser}
    ################################### TEMPORARY SOLUTION #######################################
    # We should loop over the files in the vcf directory later
    case_1_path = os.path.join(project_root, 'tests/vcf_examples/1/1.ped')
    case_2_path = os.path.join(project_root, 'tests/vcf_examples/2/2.ped')

    variants_1_path = os.path.join(project_root, 'tests/vcf_examples/1/test_vcf.vcf')
    variants_2_path = os.path.join(project_root, 'tests/vcf_examples/2/test_vcf.vcf')

    ##############################################################################################
    cases_path = os.path.join(project_root, 'tests/vcf_examples')
    for root, dirs, files in os.walk(cases_path):
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

    self._cases.append(self.get_case(case_1_path))
    self._cases.append(self.get_case(case_2_path))

    self._variants['1'] = vcf_parser.VCFParser(infile = variants_1_path)
    self._variants['2'] = vcf_parser.VCFParser(infile = variants_2_path)


  def get_case(self, case_file):
    """Take a case file and return the case on the specified format."""
    case_parser = ped_parser.FamilyParser(case_file)
    return case_parser.get_json()[0]
  
  
  def cases(self):
    return self._cases

  def case(self, case_id):
    for case in self._cases:
      if case['id'] == case_id:
        return case
  
  def variants(self, case, query=None, variant_ids=None, nr_of_variants = 100):
  
    # if variant_ids:
    #   return self._many_variants(variant_ids)
    def format_variant(variant):
      """Return the variant in a format specified for scout."""
      return variant

    variants = []
    i = 0
    for variant in self._variants[case]:
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
    print(my_vcf._cases)
    my_vcf.init_app('app')
    for variant in my_vcf.variants('1'):
      print(variant)

if __name__ == '__main__':
    cli()
