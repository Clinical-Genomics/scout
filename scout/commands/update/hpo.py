import logging
import click
import urllib.request

from pprint import pprint as pp

from scout.load.hpo import load_hpo_terms
from scout.utils.requests import (fetch_hpo_terms, fetch_hpo_to_genes)

LOG = logging.getLogger(__name__)

@click.command('hpo', short_help='Update hpo terms')
@click.option('--update',
    is_flag=True,
    help="If existing terms should be updated"
)
@click.pass_context
def hpo(context, update):
    """
    Update the hpo terms in the database. Fetch the latest release and update terms.
    """
    LOG.info("Running scout update hpo")
    adapter = context.obj['adapter']
    
    existing_terms = adapter.hpo_terms()
    if existing_terms.count() > 0:
        if not update:
            LOG.warning("HPO terms are already loaded, use '--update' to load new")
            context.abort()
        
        LOG.info("Dropping HPO terms")
        adapter.hpo_term_collection.drop()
        LOG.debug("HPO terms dropped")
    
    # Fetch the latest version of the hpo terms
    hpo_lines = fetch_hpo_terms()
    # Fetch the connection to genes from hpo source
    hpo_gene_lines = fetch_hpo_to_genes()
    
    load_hpo_terms(adapter, hpo_lines, hpo_gene_lines)
