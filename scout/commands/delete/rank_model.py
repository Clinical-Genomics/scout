import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("rank-model", short_help="Delete a rank model from database")
@click.option("-f", "--force", is_flag=True, help="Force delete even if explicitly found on cases")
@click.argument("rank_model_url")
@with_appcontext
def rank_model(rank_model_url, force):
    """Delete a rank model from the database.

    Takes rank model URL or file path to delete from database as argument.
    Stops if the URL is found explicitly set on a case, but does not case rank model match versions and category against
    rank model candidates.
    Use force to remove the loaded model anyway.
    Links on cases stay set, and models will reload on use.
    """
    LOG.info("Running scout delete rank model")
    adapter = store

    rank_model_obj = adapter.rank_model_from_url(rank_model_url)
    if not rank_model_obj:
        LOG.warning("Rank model {0} was not found in database".format(rank_model_url))
        return

    if not force and adapter.case_collection.find_one(
        {"$or": [{"rank_model_url": rank_model_url}, {"sv_rank_model_url": rank_model_url}]}
    ):
        LOG.warning(
            "Rank model {0} is associated to one or more cases in the database. Use --force option to delete it anyway.".format(
                rank_model_url
            )
        )
        return

    result = adapter.delete_rank_model(rank_model_url)
    if result.deleted_count == 0:
        LOG.warning("Rank model delete unsuccessful")
        return

    LOG.info("Rank model delete successful")
