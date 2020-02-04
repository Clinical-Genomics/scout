import logging

from pprint import pprint as pp
from flask.cli import with_appcontext
import click

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("compounds", short_help="Update compounds for a case")
@click.argument("case_id")
@with_appcontext
def compounds(case_id):
    """
    Update all compounds for a case
    """
    adapter = store
    LOG.info("Running scout update compounds")
    # Check if the case exists
    case_obj = adapter.case(case_id)

    if not case_obj:
        LOG.warning("Case %s could not be found", case_id)
        raise click.Abort()

    try:
        adapter.update_case_compounds(case_obj)
    except Exception as err:
        LOG.warning(err)
        raise click.Abort()
