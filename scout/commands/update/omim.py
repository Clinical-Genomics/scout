import logging
import click
import urllib.request

from flask.cli import with_appcontext, current_app

from pprint import pprint as pp

from scout.parse.omim import (parse_genemap2, parse_mim2gene, parse_omim_morbid, parse_mim_titles,
                              get_mim_genes, get_mim_phenotypes)
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

@click.command('omim', short_help='Update omim gene panel')
@click.option('--api-key', help='Specify the api key')
@click.option('--institute',
    help='Specify the owner of the omim panel',
    default='cust002',
    show_default=True,
)
@with_appcontext
def omim(api_key, institute):
    """
    Update the automate generated omim gene panel in the database.
    """
    LOG.info("Running scout update omim")
    adapter = store

    api_key = api_key or current_app.config.get('OMIM_API_KEY')
    if not api_key:
        LOG.warning("Please provide a omim api key to load the omim gene panel")
        raise click.Abort()

    institute_obj = adapter.institute(institute)
    if not institute_obj:
        LOG.info("Institute %s could not be found in database", institute)
        LOG.warning("Please specify an existing institute")
        raise click.Abort()

    try:
        adapter.load_omim_panel(api_key, institute=institute)
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
