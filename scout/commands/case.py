# -*- coding: utf-8 -*-
import logging

import click

from scout.load import load_scout

logger = logging.getLogger(__name__)

@click.command()
@click.pass_context
@click.option('--vcf', 
              type=click.Path(exists=True),
              help='path to clinical VCF file to be loaded'
)
@click.option('--vcf-sv', 
              type=click.Path(exists=True),
              help='path to clinical SV VCF file to be loaded'
)
@click.option('--owner', 
              help='parent institute for the case'
)
@click.option('--ped', 
              type=click.File('r')
)
@click.option('-u', '--update', 
              is_flag=True
)
@click.argument('config', 
              type=click.File('r'), 
              required=False
)
def case(context, vcf, vcf_sv, owner, ped, update, config):
    """Load a case into the database"""
    if config is None and ped is None:
        click.echo("you have to provide either config or ped file")
        context.abort()

    config_data = yaml.load(config) if config else {}

    if not config_data:
        config_data['analysis_date'] = datetime.date.today()

    config_data['vcf_snv'] = vcf if vcf else config_data.get('vcf_snv')
    config_data['vcf_sv'] = vcf_sv if vcf_sv else config_data.get('vcf_sv')
    config_data['owner'] = owner if owner else config_data.get('owner')
    config_data['rank_treshold'] = config_data.get('rank_treshold') or 5

    from pprint import pprint as pp
    pp(config_data)
    context.abort()
    
    if not (config_data.get('vcf_snv') or config_data.get('vcf_sv')):
        logger.warn("Please provide a vcf file (use '--vcf')")
        context.abort()

    if not config_data.get('owner'):
        logger.warn("Please provide an owner for the case (use '--owner')")
        context.abort()
    
    try:
        load_scout(context.obj['adapter'], config_data, ped=ped, update=update)
    except (IntegrityError, ValueError, ConfigError, KeyError) as error:
        click.echo(error)
        context.abort()


@click.command()
@click.option('-i', '--institute', 
              help='institute id of related cases'
)
@click.option('-c', '--case_id',
                  default=None
)
@click.pass_context
def delete_case(context, institute, case_id):
    """Delete a case and it's variants from the database"""
    adapter = context.obj['adapter']
    
    if not case_id:
        click.echo("Please specify the id of the case that should be "
                       "deleted with flag '-c/--case_id'.")
        context.abort()

    if not institute:
        click.echo("Please specify the owner of the case that should be "
                       "deleted with flag '-i/--institute'.")
        context.abort()
    
    logger.info("Running deleting case {0}".format(case_id))
    
    case = adapter.delete_case(
        institute_id=institute,
        case_id=case_id
    )

    if case:
        adapter.delete_variants(case_id=case.case_id, variant_type='clinical')
        adapter.delete_variants(case_id=case.case_id, variant_type='research')
    else:
        logger.warning("Case does not exist in database")
        context.abort()
    

@click.command()
@click.option('-i', '--institute', 
              help='institute id of related cases'
)
@click.option('-r', '--reruns', 
              is_flag=True, 
              help='requested to be rerun'
)
@click.option('-f', '--finished', 
              is_flag=True, 
              help='archived or solved'
)
@click.option('--causatives', 
              is_flag=True, 
              help='Has causative variants'
)
@click.option('--research-requested', 
              is_flag=True, 
              help='If research is requested'
)
@click.option('--is-research', 
              is_flag=True, 
              help='If case is in research mode'
)
@click.pass_context
def cases(context, institute, reruns, finished, causatives, research_requested,
          is_research):
    """Interact with cases existing in the database."""
    adapter = context.obj['adapter']
    
    models = adapter.cases(collaborator=institute, reruns=reruns,
                           finished=finished, has_causatives=causatives,
                           research_requested=research_requested,
                           is_research=is_research)
    for model in models:
        click.echo(model.case_id)
