import logging

from pprint import pprint as pp

import click

LOG = logging.getLogger(__name__)


@click.command('institute', short_help='Update institute for a case')
@click.argument('internal-id')
@click.option('-c', '--coverage-cutoff')
@click.option('-s', '--sanger-recipient', )
@click.pass_context
def institute(context, internal_id, sanger_recipient, coverage_cutoff):
    """
    Update an institute
    """
    adapter = context.obj['adapter']
    LOG.info("Running scout update institute")

    # Check if the institute exists
    institute_obj = adapter.institute(internal_id)

    if not institute_obj:
        LOG.warning("institute %s could not be found", internal_id)
        context.abort()

    try:
        adapter.update_institute(internal_id=internal_id, sanger_recipient=sanger_recipient,
                                 coverage_cutoff=coverage_cutoff)
    except Exception as err:
        LOG.warning(err)
        context.abort()
