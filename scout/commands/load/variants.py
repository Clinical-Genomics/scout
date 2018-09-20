import logging
from pprint import pprint as pp

import click

LOG = logging.getLogger(__name__)

@click.command(short_help='Upload variants to existing case')
@click.argument('case-id')
@click.option('-i', '--institute', help='institute id of related cases')
@click.option('-f', '--force', is_flag=True, help='upload without request')
@click.option('--cancer', is_flag=True, help='Upload clinical cancer variants')
@click.option('--cancer-research', is_flag=True, help='Upload research cancer variants')
@click.option('--sv', is_flag=True, help='Upload clinical structural variants')
@click.option('--sv-research', is_flag=True, help='Upload research structural variants')
@click.option('--snv', is_flag=True, help='Upload clinical SNV variants')
@click.option('--snv-research', is_flag=True, help='Upload research SNV variants')
@click.option('--str-clinical', is_flag=True, help='Upload clinical STR variants')
@click.option('--chrom', help='If region, specify the chromosome')
@click.option('--start', type=int, help='If region, specify the start')
@click.option('--end', type=int, help='If region, specify the end')
@click.option('--hgnc-id', type=int, help='If all variants from a gene, specify the gene id')
@click.option('--hgnc-symbol', help='If all variants from a gene, specify the gene symbol')
@click.option('--rank-treshold', default=5, help='Specify the rank score treshold',
                show_default=True)
@click.pass_context
def variants(context, case_id, institute, force, cancer, cancer_research, sv, 
             sv_research, snv, snv_research, str_clinical, chrom, start, end, hgnc_id, 
             hgnc_symbol, rank_treshold):
    """Upload variants to a case

        Note that the files has to be linked with the case, 
        if they are not use 'scout update case'.
    """
    LOG.info("Running scout load variants")
    adapter = context.obj['adapter']
    
    if institute:
        case_id = "{0}-{1}".format(institute, case_id)
    else:
        institute = case_id.split('-')[0]
    case_obj = adapter.case(case_id=case_id)
    if case_obj is None:
        LOG.info("No matching case found")
        context.abort()

    files = [
        {'category': 'cancer', 'variant_type': 'clinical', 'upload': cancer},
        {'category': 'cancer', 'variant_type': 'research', 'upload': cancer_research},
        {'category': 'sv', 'variant_type': 'clinical', 'upload': sv},
        {'category': 'sv', 'variant_type': 'research', 'upload': sv_research},
        {'category': 'snv', 'variant_type': 'clinical', 'upload': snv},
        {'category': 'snv', 'variant_type': 'research', 'upload': snv_research},
        {'category': 'str', 'variant_type': 'clinical', 'upload': str_clinical},
    ]
    
    gene_obj = None
    if (hgnc_id or hgnc_symbol):
        if hgnc_id:
            gene_obj = adapter.hgnc_gene(hgnc_id)
        if hgnc_symbol:
            for res in adapter.gene_by_alias(hgnc_symbol):
                gene_obj = res
        if not gene_obj:
            LOG.warning("The gene could not be found")
            context.abort()
        
    i = 0
    for file_type in files:
        variant_type = file_type['variant_type']
        category = file_type['category']
        
        if file_type['upload']:
            i += 1
            if variant_type == 'research':
                if not (force or case_obj['research_requested']):
                    LOG.warn("research not requested, use '--force'")
                    context.abort()
            
            LOG.info("Delete {0} {1} variants for case {2}".format(
                         variant_type, category, case_id))
            adapter.delete_variants(case_id=case_obj['_id'], 
                                    variant_type=variant_type,
                                    category=category)
            
            LOG.info("Load {0} {1} variants for case {2}".format(
                         variant_type, category, case_id))
            
            try:
                adapter.load_variants(
                    case_obj=case_obj, 
                    variant_type=variant_type, 
                    category=category,
                    rank_threshold=rank_treshold, 
                    chrom=chrom, 
                    start=start, 
                    end=end,
                    gene_obj=gene_obj
                )
            except Exception as e:
                LOG.warning(e)
                context.abort()
    if i == 0:
        LOG.info("No files where specified to upload variants from")
