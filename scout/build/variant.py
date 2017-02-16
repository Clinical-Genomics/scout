# -*- coding: utf-8 -*-
import logging

from scout.models import Variant

from . import (build_genotype, build_compound, build_gene, build_clnsig)

log = logging.getLogger(__name__)


def build_variant(variant, institute, gene_to_panels = None, hgncid_to_gene=None):
    """Build a mongoengine Variant based on parsed information

        Args:
            variant(dict)
            institute(Institute): A mongoengine institute
            hgnc_genes(dict[HgncGene])

        Returns:
            variant_obj(Variant)
    """
    gene_to_panels = gene_to_panels or {}
    hgncid_to_gene = hgncid_to_gene or {}

    variant_obj = Variant(
        document_id=variant['ids']['document_id'],
        variant_id=variant['ids']['variant_id'],
        display_name=variant['ids']['display_name'],
        variant_type=variant['variant_type'],
        case_id=variant['case_id'],
        chromosome=variant['chromosome'],
        position=variant['position'],
        reference=variant['reference'],
        alternative=variant['alternative'],
        rank_score=variant['rank_score'],
        institute=institute,
    )
    variant_obj['simple_id'] = variant['ids'].get('simple_id')

    variant_obj['quality'] = variant['quality']
    variant_obj['filters'] = variant['filters']

    variant_obj['end'] = variant.get('end')
    variant_obj['length'] = variant.get('length')
    variant_obj['dbsnp_id'] = variant.get('dbsnp_id')

    variant_obj['category'] = variant.get('category')
    variant_obj['sub_category'] = variant.get('sub_category')

    variant_obj['mate_id'] = variant.get('mate_id')

    gt_types = []
    for sample in variant.get('samples', []):
        gt_call = build_genotype(sample)
        gt_types.append(gt_call)

    variant_obj['samples'] = gt_types

    variant_obj.genetic_models = variant.get('genetic_models')

    # Add the compounds
    compounds = []
    for compound in variant.get('compounds', []):
        compound_obj = build_compound(compound)
        compounds.append(compound_obj)
    variant_obj['compounds'] = compounds

    # Add the genes with transcripts
    genes = []
    for index, gene in enumerate(variant.get('genes', [])):
        gene_obj = build_gene(gene)
        genes.append(gene_obj)
        if index > 30:
            # avoid uploading too much data (specifically for SV variants)
            # mark variant as missing data
            variant_obj['missing_data'] = True
            break

    variant_obj['genes'] = genes

    variant_obj['hgnc_ids'] = variant.get('hgnc_ids')

    # Add the hgnc symbols from the database genes
    hgnc_symbols = []
    for hgnc_id in variant_obj['hgnc_ids']:
        gene_obj = hgncid_to_gene.get(hgnc_id)
        if gene_obj:
            hgnc_symbols.append(gene_obj.hgnc_symbol)
        else:
            log.warn("missing HGNC symbol for: %s", hgnc_id)

    variant_obj['hgnc_symbols'] = hgnc_symbols

    # link gene panels
    panel_names = set()
    for hgnc_id in variant_obj['hgnc_ids']:
        gene_panels = gene_to_panels.get(hgnc_id, set())
        panel_names = panel_names.union(gene_panels)

    variant_obj['panels'] = list(panel_names)

    # Add the clnsig ocbjects
    clnsig_objects = []
    for entry in variant.get('clnsig', []):
        clnsig_obj = build_clnsig(entry)
        clnsig_objects.append(clnsig_obj)
    variant_obj['clnsig'] = clnsig_objects

    # Add the callers
    call_info = variant.get('callers', {})
    variant_obj['gatk'] = call_info.get('gatk')
    variant_obj['samtools'] = call_info.get('samtools')
    variant_obj['freebayes'] = call_info.get('freebayes')

    # Add the conservation
    conservation_info = variant.get('conservation', {})
    variant_obj['phast_conservation'] = conservation_info.get('phast', [])
    variant_obj['gerp_conservation'] = conservation_info.get('gerp', [])
    variant_obj['phylop_conservation'] = conservation_info.get('phylop', [])

    # Add the frequencies
    frequencies = variant.get('frequencies', {})
    variant_obj['thousand_genomes_frequency'] = frequencies.get('thousand_g')
    variant_obj['thousand_genomes_frequency_left'] = frequencies.get('thousand_g_left')
    variant_obj['thousand_genomes_frequency_right'] = frequencies.get('thousand_g_right')
    variant_obj['exac_frequency'] = frequencies.get('exac')
    variant_obj['max_thousand_genomes_frequency'] = frequencies.get('thousand_g_max')
    variant_obj['max_exac_frequency'] = frequencies.get('exac_max')

    # add the local observation counts from the old archive
    variant_obj['local_obs_old'] = variant.get('local_obs_old')
    variant_obj['local_obs_hom_old'] = variant.get('local_obs_hom_old')

    # Add the severity predictors

    variant_obj['cadd_score'] = variant.get('cadd_score')
    variant_obj['spidex'] = variant.get('spidex')

    # Add the rank score results
    rank_results = []
    for category in variant.get('rank_result', []):
        rank_result = {
            'category': category,
            'score': variant['rank_result'][category]
        }
        rank_results.append(rank_result)

    variant_obj['rank_score_results'] = rank_results

    return variant_obj
