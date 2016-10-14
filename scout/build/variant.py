from scout.models import Variant

from . import (build_genotype, build_compound, build_gene)
        
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

    variant_obj['end'] = variant.get('end')
    variant_obj['length'] = variant.get('length')
    variant_obj['db_snp_ids'] = variant.get('db_snp_ids')
    
    variant_obj['category'] = variant.get('category')
    variant_obj['sub_category'] = variant.get('sub_category')

    variant_obj['mate_id'] = variant.get('mate_id')
    
    gt_types = []
    for sample in variant['samples']:
        gt_call = build_genotype(sample)
        gt_types.append(gt_call)
    variant_obj['samples'] = gt_types
    
    variant_obj.genetic_models = variant['genetic_models']
    
    # Add the compounds
    compounds = []
    for compound in variant['compounds']:
        compound_obj = build_compound(compound)
        compounds.append(compound_obj)
    variant_obj['compounds'] = compounds
    
    # Add the genes with transcripts
    genes = []
    for gene in variant['genes']:
        gene_obj = build_gene(gene)
        genes.append(gene_obj)
    variant_obj['genes'] = genes
    
    # Add the callers
    call_info = variant.get('callers', {})
    variant_obj['gatk'] = call_info.get('gatk')
    variant_obj['samtools'] = call_info.get('samtools')
    variant_obj['freebayes'] = call_info.get('freebayes')
    
    # Add the conservation
    conservation_info = variant.get('conservation', {})
    variant_obj['phast_conservation'] = conservation_info.get('phast',[])
    variant_obj['gerp_conservation'] = conservation_info.get('gerp',[])
    variant_obj['phylop_conservation'] = conservation_info.get('phylop',[])
    
    variant_obj['gene_lists'] = variant.get('gene_lists')
    variant_obj['expected_inheritance'] = variant.get('expected_inheritance')
    
    return variant_obj