#!/usr/bin/env python
# encoding: utf-8
"""
get_mongo_variant.py

Create a mongo engine variant object from a variant dictionary.

Created by Måns Magnusson on 2014-11-10.
Copyright (c) 2014 __MoonsoInc__. All rights reserved.

"""

from __future__ import (absolute_import, print_function,)

import sys
import os
import logging

from scout.models import (Variant, Institute)
from scout._compat import iteritems

from . import (get_genes, get_genotype, get_compounds, generate_md5_key)

logger = logging.getLogger(__name__)

def get_mongo_variant(variant, variant_type, individuals, case, institute, 
                        variant_count):
    """
    Take a variant and some additional information, convert it to mongo engine
    objects and put them in the proper format in the database.
    
    Input:
        variant (dict): A Variant dictionary
        variant_type  (str): A string in ['clinical', 'research']
        individuals   (dict): A dictionary with the id:s of the individuals as keys and
                      display names as values
        case (Case): The Case object that the variant belongs to
        institute(Institute): A institute object
        variant_count (int): The rank order of the variant in this case
    
    Returns:
        mongo_variant : A variant parsed into the proper mongoengine format.
    
    """
    # Create the ID for the variant
    case_id = case.case_id
    case_name = case.display_name
    
    id_fields = [
                  variant['CHROM'],
                  variant['POS'],
                  variant['REF'],
                  variant['ALT'],
                  variant_type
                ]
    
    # We need to create md5 keys since REF and ALT can be huge:
    variant_id = generate_md5_key(id_fields)
    document_id = generate_md5_key(id_fields+case_id.split('_'))

    # Create the mongo variant object
    mongo_variant = Variant(
                          document_id = document_id,
                          variant_id = variant_id,
                          variant_type = variant_type,
                          case_id = case_id,
                          display_name = '_'.join(id_fields),
                          chromosome = variant['CHROM'],
                          position = int(variant['POS']),
                          reference = variant['REF'],
                          alternative = variant['ALT'],
                          variant_rank = variant_count,
                          quality = float(variant['QUAL']),
                          filters = variant['FILTER'].split(';'),
                          institute = institute
                  )

    # If a variant belongs to any gene lists we check which ones
    gene_lists = variant['info_dict'].get('Clinical_db_gene_annotation')
    if gene_lists:
        logger.info("Adding gene lists {0}".format(set(gene_lists)))
        mongo_variant['gene_lists'] = list(set(gene_lists))
    
    ################# Add the rank score and variant rank #################
    # Get the rank score as specified in the config file.
    # This is central for displaying variants in scout.

    mongo_variant['rank_score'] = float(
      variant.get('rank_scores', {}).get(case_name, 0.0)
    )

    ################# Add gt calls #################
    gt_calls = []
    for individual_id, display_name in iteritems(individuals):
        # This function returns an ODM GTCall object with the
        # relevant information for a individual:
        gt_calls.append(get_genotype(
                                      variant,
                                      individual_id,
                                      display_name
                                    )
                                )
    mongo_variant['samples'] = gt_calls

    ################# Add the compound information #################

    mongo_variant['compounds'] = get_compounds(
                                          variant,
                                          case,
                                          variant_type
                                        )
                                    
    ################# Add the inheritance patterns #################

    mongo_variant['genetic_models'] = variant.get(
                                        'genetic_models',
                                        {}
                                        ).get(
                                            case_name,
                                            []
                                            )

    ################# Add the gene and tanscript information #################

    # Get genes return a list with ODM objects for each gene
    mongo_variant['genes'] = get_genes(variant)
    hgnc_symbols = set([])
    ensembl_gene_ids = set([])
    
    # Add the clinsig prediction
    clnsig = variant.get('CLNSIG', None)
    clnsig_accession = variant.get('SnpSift_CLNACC', None)
    if clnsig:
        clnsig = clnsig[0].split('|')
        try:
            for index, clnsig_entry in enumerate(clnsig):
                if int(clnsig_entry) == 5:
                    mongo_variant['clnsig'] = 5
                    if clnsig_accession:
                        clnsig_accession = clnsig_accession[0].split('|')
                        mongo_variant['clnsigacc'] = clnsig_accession[index]
        except (ValueError, IndexError):
            pass

    for gene in mongo_variant.genes:
        hgnc_symbols.add(gene.hgnc_symbol)
        ensembl_gene_ids.add(gene.ensembl_gene_id)

    mongo_variant['hgnc_symbols'] = list(hgnc_symbols)

    mongo_variant['ensembl_gene_ids'] = list(ensembl_gene_ids)

    ################# Add a list with the dbsnp ids #################

    mongo_variant['db_snp_ids'] = variant['ID'].split(';')

    ################# Add the frequencies #################

    try:
        mongo_variant['thousand_genomes_frequency'] = float(
                                variant['info_dict'].get(
                                  config_object['VCF']['1000GMAF']['vcf_info_key'],
                                  ['0'])[0]
                                )
    except ValueError:
        pass

    try:
        mongo_variant['exac_frequency'] = float(
                                variant['info_dict'].get(
                                  config_object['VCF']['EXAC']['vcf_info_key'],
                                  ['0'])[0]
                                )
    except ValueError:
        pass

    # Add the severity predictions
    mongo_variant['cadd_score'] = float(
                          variant['info_dict'].get(
                            config_object['VCF']['CADD']['vcf_info_key'],
                            ['0'])[0]
                          )
    # Add conservation annotation
    mongo_variant['gerp_conservation'] = variant['info_dict'].get(
                                  config_object['VCF']['Gerp']['vcf_info_key'],
                                  []
                                )
    mongo_variant['phast_conservation'] = variant['info_dict'].get(
                                  config_object['VCF']['PhastCons']['vcf_info_key'],
                                  []
                                )
    mongo_variant['phylop_conservation'] = variant['info_dict'].get(
                                  config_object['VCF']['PhylopCons']['vcf_info_key'],
                                  []
                                )

    return mongo_variant

