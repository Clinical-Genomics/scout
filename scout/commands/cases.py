# -*- coding: utf-8 -*-
import logging

import click

log = logging.getLogger(__name__)


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
@click.option('--delete',
              is_flag=True,
              help="Delete a case from the database"
)
@click.option('-c', '--case_id',
              default=None
)
@click.pass_context
def cases(context, institute, reruns, finished, delete, case_id):
    """Interact with cases in the database."""
    adapter = context.obj['adapter']
    
    if delete:
        if not case_id:
            logger.warning("Please specify the id of the case that should be "
                           "deleted with flag '-c/--case_id'.")
            ctx.abort()

        if not institute:
            logger.warning("Please specify the owner of the case that should be "
                           "deleted with flag '-i/--institute'.")
            ctx.abort()
        
        logger.info("Running deleting case {0}".format(case_id))
        
        case = adapter.delete_case(
            institute_id=institute,
            case_id=case_id
        )

        if case:
            logger.info("Delete the clinical variants for case {0}".format(
                        case.case_id))
            adapter.delete_variants(case_id=case.case_id, variant_type='clinical')
            logger.info("Delete the research variants for case {0}".format(
                        case.case_id))
            adapter.delete_variants(case_id=case.case_id, variant_type='research')
        
    else:
        models = adapter.cases(collaborator=institute, reruns=reruns,
                           finished=finished)
        for model in models:
            click.echo(model.owner_case_id)
