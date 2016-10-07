from scout.models import Variant

from . import (build_genotype)

def build_variant(variant, institute):
    """Build a mongoengine Variant based on parsed information
    
        Args:
            variant(dict)
            institute(Institute): A mongoengine institute
    
        Returns:
            variant_obj(Variant)
    """
    variant_obj = Variant(
        document_id = variant['ids']['document_id'],
        variant_id = variant['ids']['variant_id'],
        display_name = variant['ids']['display_name'],
        variant_type = variant['variant_type'],
        case_id = variant['case_id'],
        chromosome = variant['chromosome'],
        position = variant['position'],
        reference = variant['reference'],
        alternative = variant['alternative'],
        rank_score = variant['rank_score'],
        institute = institute,
    )
    variant_obj['simple_id'] = variant['ids'].get('simple_id')
    
    variant_obj['quality'] = variant['quality']
    variant_obj['filters'] = variant['filters']
    
    gt_types = []
    for sample in variant['samples']:
        gt_call = build_genotype(sample)
        gt_types.append(gt_call)
    variant_obj.samples = gt_types
    
    variant_obj.genetic_models = variant['genetic_models']
    
    compounds = []
    for compound in variant['compounds']:
        compound_obj = build_compound(compound)
        compounds.append(compound_obj)
    variant_obj.compounds = compounds
    
    genes = []
    for gene in variant['genes']:
        gene_obj = build_gene(gene)
        genes.append(gene_obj)
    variant_obj.genes = genes