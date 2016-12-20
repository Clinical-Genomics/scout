import logging

import click

from scout.load.variant import load_variants

logger = logging.getLogger(__name__)

@click.command('research', short_help='Upload research variants')
@click.option('--case-id',
                  default=None
)
@click.option('-i', '--institute', 
              help='institute id of related cases'
)
@click.pass_context
def research(context, case_id, institute):
    """Upload research variants to cases
    
        If a case is specified, all variants found for that case will be 
        uploaded.
    
        If no cases are specified then all cases that have 'research_requested'
        will have there research variants uploaded
    """
    logger.info("Running scout load research")
    adapter = context.obj['adapter']
    
    if (case_id or institute):
        if not institute:
            logger.info("Please specify a institute")
            context.abort()
        if not case_id:
            logger.info("Please specify a case id")
            context.abort()
        case_objs = case(
            institute_id=institute, 
            case_id=case_id
        )
    #Fetch all cases that have requested research
    else:
        case_objs = adapter.cases(research_requested=research_requested)
    
    if not case_objs:
        logger.info("No matching cases could be found")
        context.abort()
    
    for case_obj in case_objs:
        if case_obj.research_requested:
            logger.info("Loading research snvs for case {}".format(case_obj.case_id))
            load_variants(
                adapter=adapter, 
                variant_file=case_obj.vcf_files['vcf_snv_research'], 
                case_obj=case_obj, 
                variant_type='research',
                category='snv', 
                rank_treshold=case_obj.rank_score_treshold, 
            )
            if case_obj.vcf_files.get('vcf_sv_research'):
                logger.info("Loading research svs for case {}".format(case_obj.case_id))
                load_variants(
                    adapter=adapter, 
                    variant_file=case_obj.vcf_files['vcf_sv_research'], 
                    case_obj=case_obj, 
                    variant_type='research',
                    category='sv', 
                    rank_treshold=case_obj.rank_score_treshold, 
                )
        click.echo('\t'.join([panel_obj.panel_name, str(panel_obj.version)]))
