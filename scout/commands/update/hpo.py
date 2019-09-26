import logging
import click

from pprint import pprint as pp
from flask.cli import with_appcontext

from scout.load.hpo import load_hpo_terms

from scout.commands.utils import abort_if_false
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

@click.command('hpo', short_help='Update hpo terms')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to drop the hpo terms?')
@with_appcontext
def hpo():
    """
    Update the hpo terms in the database. Fetch the latest release and update terms.
    """
    LOG.info("Running scout update hpo")
    adapter = store

    LOG.info("Dropping HPO terms")
    adapter.hpo_term_collection.drop()
    LOG.debug("HPO terms dropped")

    load_hpo_terms(adapter)
