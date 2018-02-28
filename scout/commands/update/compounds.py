import logging

from pprint import pprint as pp

import click

LOG = logging.getLogger(__name__)

@click.command('compounds', short_help='Update compounds for a case')
@click.argument('case_id')
@click.pass_context
def compounds(context, case_id):
    """
    Update all compounds for a case
    """
    adapter = context.obj['adapter']
    LOG.info("Running scout update compounds")
    # Check if the case exists
    case_obj = adapter.case(case_id)
    
    if not case_obj:
        LOG.warning("Case %s could not be found", case_id)
        context.abort()
    
    try:
        adapter.update_case_compounds(case_obj)
    except Exception as err:
        LOG.warning(err)
        context.abort()
