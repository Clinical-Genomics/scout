import logging
import click
import urllib.request

from pprint import pprint as pp

from scout.load.hpo import load_hpo_terms
from scout.utils.requests import (fetch_hpo_terms, fetch_hpo_to_genes)

from scout.commands.utils import abort_if_false

LOG = logging.getLogger(__name__)

@click.command('hpo', short_help='Update hpo terms')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to drop the hpo terms?')
@click.pass_context
def hpo(context):
    """
    Update the hpo terms in the database. Fetch the latest release and update terms.
    """
    LOG.info("Running scout update hpo")
    adapter = context.obj['adapter']

    LOG.info("Dropping HPO terms")
    adapter.hpo_term_collection.drop()
    LOG.debug("HPO terms dropped")

    load_hpo_terms(adapter)
