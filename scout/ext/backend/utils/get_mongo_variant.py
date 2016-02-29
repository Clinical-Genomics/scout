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

def get_clnsig(variant):
    """Get the clnsig information

        We are only interested when clnsig = 5. So for each 5 we return the
        CLNSIG accesson number.

        Args:
            variant (dict): A Variant dictionary

        Returns:
            clnsig_accsessions(list)
    """
    clnsig_key = 'SnpSift_CLNSIG'
    accession_key = 'SnpSift_CLNACC'
    clnsig_annotation = variant['info_dict'].get(clnsig_key)
    accession_annotation = variant['info_dict'].get(accession_key)

    clnsig_accsessions = []
    if clnsig_annotation:
        clnsig_annotation = clnsig_annotation[0].split('|')
        logger.debug("Found clnsig annotations {0}".format(
            ', '.join(clnsig_annotation)))
        try:
            accession_annotation = (accession_annotation or [])[0].split('|')
            for index, entry in enumerate(clnsig_annotation):
                if int(entry) == 5:
                    if accession_annotation:
                        clnsig_accsessions.append(accession_annotation[index])
        except (ValueError, IndexError):
            pass

    return clnsig_accsessions


def get_mongo_variant(variant, variant_type, individuals, case, institute,
                        variant_count):
    """
    Take a variant and some additional information, convert it to mongo engine
    objects and put them in the proper format in the database.

    Args:
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
        logger.debug("Adding gene lists {0} to variant {1}".format(
            set(gene_lists), variant['variant_id']))
        mongo_variant['gene_lists'] = list(set(gene_lists))

    ################# Add the rank score and variant rank #################
    # The rank score is central for displaying variants in scout.

    rank_score = float(variant.get('rank_scores', {}).get(case_name, 0.0))
    mongo_variant['rank_score'] = rank_score
    logger.debug("Updating rank score for variant {0} to {1}".format(
        variant['variant_id'], rank_score))

    ################# Add gt calls #################
    gt_calls = []
    for individual_id, display_name in iteritems(individuals):
        # This function returns an ODM GTCall object with the
        # relevant information for a individual:
        gt_calls.append(get_genotype(
                                      variant=variant,
                                      individual_id=individual_id,
                                      display_name=display_name
                                    )
                                )
    logger.debug("Updating genotype calls for variant {0}".format(
        variant['variant_id']))
    mongo_variant['samples'] = gt_calls

    ################# Add the compound information #################
    logger.debug("Updating compounds for variant {0}".format(
        variant['variant_id']))

    mongo_variant['compounds'] = get_compounds(
                                          variant=variant,
                                          case=case,
                                          variant_type=variant_type
                                        )

    ################# Add the inheritance patterns #################

    genetic_models = variant.get('genetic_models',{}).get(case_name,[])
    mongo_variant['genetic_models'] = genetic_models
    logger.debug("Updating genetic models for variant {0} to {1}".format(
        variant['variant_id'], ', '.join(genetic_models)))
        
    # Add the expected inheritance patterns
    
    expected_inheritance = variant['info_dict'].get('Genetic_disease_model')
    if expected_inheritance:
        mongo_variant['expected_inheritance'] = expected_inheritance

    # Add the clinsig prediction
    clnsig_accessions = get_clnsig(variant)
    if clnsig_accessions:
        logger.debug("Updating clnsig for variant {0} to {1}".format(
            variant['variant_id'], '5'))
        mongo_variant['clnsig'] = 5
        logger.debug("Updating clnsigacc for variant {0} to {1}".format(
            variant['variant_id'], ', '.join(clnsig_accessions)))
        mongo_variant['clnsigacc'] = clnsig_accessions

    ################# Add the gene and transcript information #################

    # Get genes return a list with ODM objects for each gene
    mongo_variant['genes'] = get_genes(variant)
    hgnc_symbols = set([])
    ensembl_gene_ids = set([])

    for gene in mongo_variant.genes:
        hgnc_symbols.add(gene.hgnc_symbol)
        ensembl_gene_ids.add(gene.ensembl_gene_id)

    mongo_variant['hgnc_symbols'] = list(hgnc_symbols)

    mongo_variant['ensembl_gene_ids'] = list(ensembl_gene_ids)

    ################# Add a list with the dbsnp ids #################

    mongo_variant['db_snp_ids'] = variant['ID'].split(';')

    ################# Add the frequencies #################


    thousand_g = variant['info_dict'].get('1000GAF')
    if thousand_g:
        value = thousand_g[0]
        logger.debug("Updating 1000G freq for variant {0} to {1}".format(
            variant['variant_id'], value))
        mongo_variant['thousand_genomes_frequency'] = float(value)

    thousand_g_max = variant['info_dict'].get('1000G_MAX_AF')
    if thousand_g_max:
        value = thousand_g_max[0]
        logger.debug("Updating 1000G max freq for variant {0} to {1}".format(
            variant['variant_id'], value))
        mongo_variant['max_thousand_genomes_frequency'] = float(value)

    exac = variant['info_dict'].get('EXACAF')
    if exac:
        value = exac[0]
        logger.debug("Updating EXAC freq for variant {0} to {1}".format(
            variant['variant_id'], value))
        mongo_variant['exac_frequency'] = float(value)

    max_exac = variant['info_dict'].get('ExAC_MAX_AF')
    if max_exac:
        value = max_exac[0]
        logger.debug("Updating EXAC max freq for variant {0} to {1}".format(
            variant['variant_id'], value))
        mongo_variant['max_exac_frequency'] = float(value)

    # Add the severity predictions
    cadd = variant['info_dict'].get('CADD')
    if cadd:
        value = cadd[0]
        logger.debug("Updating CADD score for variant {0} to {1}".format(
            variant['variant_id'], value))
        mongo_variant['cadd_score'] = float(value)

    # Add conservation annotation
    gerp = variant['info_dict'].get('GERP++_RS_prediction_term')
    if gerp:
        logger.debug("Updating Gerp annotation for variant {0} to {1}".format(
            variant['variant_id'], ''.join(gerp)))
        mongo_variant['gerp_conservation'] = gerp

    phast_cons = variant['info_dict'].get('phastCons100way_vertebrate_prediction_term')
    if phast_cons:
        logger.debug("Updating Phast annotation for variant {0} to {1}".format(
            variant['variant_id'], ''.join(phast_cons)))
        mongo_variant['phast_conservation'] = phast_cons

    phylop = variant['info_dict'].get('phyloP100way_vertebrate_prediction_term')
    if phylop:
        logger.debug("Updating Phylop annotation for variant {0} to {1}".format(
            variant['variant_id'], ''.join(phylop)))
        mongo_variant['phylop_conservation'] = phylop

    return mongo_variant

