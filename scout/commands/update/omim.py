import logging
import click
import urllib.request

from pprint import pprint as pp

from scout.parse.omim import (parse_genemap2, parse_mim2gene, parse_omim_morbid, parse_mim_titles,
                              get_mim_genes, get_mim_phenotypes)

LOG = logging.getLogger(__name__)

@click.command('omim', short_help='Update omim gene panel')
@click.option('--api-key', help='Specify the api key')
@click.option('--institute', 
    help='Specify the owner of the omim panel',
    default='cust002',
    show_default=True,
)
@click.pass_context
def omim(context, api_key, institute):
    """
    Update the automate generated omim gene panel in the database.
    """
    LOG.info("Running scout update omim")
    adapter = context.obj['adapter']
    
    api_key = api_key or context.obj.get('omim_api_key')
    if not api_key:
        LOG.warning("Please provide a omim api key to load the omim gene panel")
        context.abort()
    
    institute_obj = adapter.institute(institute)
    if not institute_obj:
        LOG.info("Institute %s could not be found in database", institute)
        LOG.warning("Please specify an existing institute")
        context.abort()

    try:
        adapter.load_omim_panel(api_key, institute=institute)
    except Exception as err:
        LOG.error(err)
        context.abort()
    
    