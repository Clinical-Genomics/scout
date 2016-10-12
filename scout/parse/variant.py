import logging

from scout.utils import generate_md5_key
from . import (parse_genotypes, parse_compounds, get_clnsig, parse_genes, 
               parse_frequencies, parse_conservations, parse_ids, parse_callers)

from scout.exceptions import VcfError

logger=logging.getLogger(__name__)

def parse_variant(variant_dict, case, variant_type='clinical'):
    """Return a parsed variant
    
        Get all the necessary information to build a variant object
    
        Args:
            variant_dict(dict): A dictionary from VCFParser
            case(dict)
            variant_type(str): 'clinical' or 'research'
    """
    variant = {}
    # Create the ID for the variant
    case_id = case['case_id']
    case_name = case['display_name']

    variant['ids'] = parse_ids(variant_dict, case, variant_type)
    variant['case_id'] = case_id
    # type can be 'clinical' or 'research'
    # category is sv or snv
    if variant_dict['info_dict'].get('SVTYPE'):
        variant['category'] = 'sv'
    else:
        variant['category'] = 'snv'
    #sub category is 'snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv'
    # 'snv' and 'indel' are subcatogories of snv
    variant['sub_category'] = None

    ################# General information #################

    variant['reference'] = variant_dict['REF']
    variant['alternative'] = variant_dict['ALT']
    variant['quality'] = float(variant_dict['QUAL'])
    variant['filters'] = variant_dict['FILTER'].split(';')
    variant['variant_type'] = variant_type
    # This is the id of other position in translocations
    variant['mate_id'] = None
    
    ################# Position specific #################
    variant['chromosome'] = variant_dict['CHROM']
    # position = start
    variant['position'] = int(variant_dict['POS'])
    if variant['category'] == 'snv':
        ref_len = len(variant['reference'])
        alt_len = len(variant['alternative'])
        if ref_len == alt_len:
            variant['end'] = variant['position']
            variant['length'] = 1
            variant['sub_category'] = 'snv'
        elif ref_len > alt_len:
            variant['length'] = ref_len - alt_len 
            variant['end'] = variant['position'] + (ref_len - 1)
            variant['sub_category'] = 'indel'
        elif ref_len < alt_len:
            variant['length'] = alt_len - ref_len
            variant['end'] = variant['position'] + (alt_len - 1)
            variant['sub_category'] = 'indel'
    elif variant['category'] == 'sv':
        try:
            variant['sub_category'] = variant_dict['info_dict']['SVTYPE'][0]
        except KeyError:
            raise VcfError("SVs has to have SVTYPE")
        if variant['sub_category'] == 'BND':
            if variant_dict['info_dict'].get('MATEID'):
                variant['mate_id'] = variant_dict['info_dict']['MATEID'][0]
            #For translocations we set lenth to infinity
            variant_dict['length'] = float('inf')
        else:
            try:
                variant['length'] = int(variant_dict['info_dict']['SVLEN'][0])
                variant['end'] = int(variant_dict['info_dict']['END'][0])
            except KeyError:
                raise VcfError("Non BND SVs has to have SVLEN and END")
        

    ################# Gene Lists #################
    # If a variant belongs to any gene lists we check which ones
    gene_lists = variant_dict['info_dict'].get('Clinical_db_gene_annotation')
    if gene_lists:
        variant['gene_lists'] = list(set(gene_lists))
    else:
        variant['gene_lists'] = None
    
    ################# Add the rank score #################
    # The rank score is central for displaying variants in scout.

    rank_score = float(variant_dict.get('rank_scores', {}).get(case_name, 0.0))
    variant['rank_score'] = rank_score
    
    ################# Add gt calls #################
    
    variant['samples'] = parse_genotypes(variant_dict, case)
    
    ################# Add the compound information #################
    
    variant['compounds'] = parse_compounds(
                                variant=variant_dict,
                                case=case,
                                variant_type=variant_type
                                )
    
    ################# Add the inheritance patterns #################

    genetic_models = variant_dict.get('genetic_models',{}).get(case_name,[])
    variant['genetic_models'] = genetic_models

    expected_inheritance = variant_dict['info_dict'].get('Genetic_disease_model')
    if expected_inheritance:
        variant['expected_inheritance'] = expected_inheritance
    else:
        variant['expected_inheritance'] = None
    
    # Add the clinsig prediction
    clnsig_accessions = get_clnsig(variant_dict)
    if clnsig_accessions:
        variant['clnsig'] = 5
        variant['clnsigacc'] = clnsig_accessions
    else:
        variant['clnsig'] = None
        variant['clnsigacc'] = None

    ################# Add the gene and transcript information #################

    variant['genes'] = parse_genes(variant_dict)

    hgnc_symbols = set([])
    ensembl_gene_ids = set([])
    
    for gene in variant['genes']:
        hgnc_symbols.add(gene['hgnc_symbol'])
        ensembl_gene_ids.add(gene['ensembl_gene_id'])
    
    variant['hgnc_symbols'] = list(hgnc_symbols)
    variant['ensembl_gene_ids'] = list(ensembl_gene_ids)

    ################# Add a list with the dbsnp ids #################

    variant['db_snp_ids'] = variant_dict['ID'].split(';')

    ################# Add the frequencies #################
    
    variant['frequencies'] = parse_frequencies(variant_dict)

    # Add the severity predictions
    cadd = variant_dict['info_dict'].get('CADD')
    if cadd:
        value = cadd[0]
        variant['cadd_score'] = float(value)

    spidex = variant_dict['info_dict'].get('SPIDEX')
    if spidex:
        value = spidex[0]
        variant['spidex'] = spidex
    
    variant['conservation'] = parse_conservations(variant_dict)
    
    variant['callers'] = parse_callers(variant_dict)

    return variant
    
    
    
    
    