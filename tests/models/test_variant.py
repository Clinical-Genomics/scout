# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from scout.models import Variant
from scout.ext.backend.utils import generate_md5_key


def setup_variant(**kwargs):
  """
  Setup a Variant object
  """
  variant_id = kwargs.get('variant_id', '1_132_A_C')
  
  variant = Variant(
    document_id = kwargs.get('document_id', 'institute_genelist_caseid_variantid'),
    variant_id = generate_md5_key(variant_id.split('_')),
    display_name = variant_id,
    variant_type = kwargs.get('document_id', 'clinical'),
    case_id = kwargs.get('case_id', 'institute1_1'),
    chromosome = kwargs.get('chromosome', '1'),
    position = kwargs.get('position', 132),
    reference = kwargs.get('reference', 'A'),
    alternative = kwargs.get('alternative', 'C'),
    rank_score = kwargs.get('rank_score', 19),
    variant_rank = kwargs.get('variant_rank', 1),
    quality = kwargs.get('quality', 88),
    filters = kwargs.get('filters', ['PASS']),
    samples = kwargs.get('samples', []),
    genetic_models = kwargs.get('genetic_models', ['AD', 'AD_dn']),
    compounds = kwargs.get('compounds', []),
    genes = kwargs.get('genes', []),
    db_snp_ids = kwargs.get('db_snp_ids', ['rs0001']),
    # Gene ids:
    hgnc_symbols = kwargs.get('hgnc_symbols', ['ADK']),
    ensembl_gene_ids = kwargs.get('ensembl_gene_ids', ['ENSG00000156110']),
    # Frequencies:
    thousand_genomes_frequency = kwargs.get('thousand_genomes_frequency', 0.001),
    exac_frequency = kwargs.get('thousand_genomes_frequency', 0.002),
    local_frequency = kwargs.get('local_frequency', None),
    # Predicted deleteriousness:
    cadd_score = kwargs.get('cadd_score', 22),
    clnsig = kwargs.get('clnsig', 1),
    phast_conservation = kwargs.get('phast_conservation', []),
    gerp_conservation = kwargs.get('gerp_conservation', []),
    phylop_conservation = kwargs.get('phylop_conservation', []),
    # Database options:
    gene_lists = kwargs.get('gene_lists', ['gene_list_1', 'gene_list_2']),
    expected_inheritance = kwargs.get('expected_inheritance', ['AR']),
    manual_rank = kwargs.get('manual_rank', 5),
    acmg_evaluation = kwargs.get('acmg_evaluation', None),
    
  )

  return variant
  
def test_variant():
  """
  Test the variant class
  """
  variant = setup_variant()
  
  assert variant.document_id == 'institute_genelist_caseid_variantid'
  assert variant.variant_id == generate_md5_key('1_132_A_C'.split('_'))
  assert variant.manual_rank == 5
  assert variant.manual_rank_level == 'high'
  
  
  
  
  
