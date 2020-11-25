import logging
import json as json_lib


from pprint import pprint as pp

from flask.cli import with_appcontext

import click

from scout.constants import CASE_STATUSES
from scout.server.extensions import store
from .utils import json_option
from .export_handler import bson_handler

LOG = logging.getLogger(__name__)


@click.command("cases", short_help="Fetch cases")
@click.option("--case-id", help="Case id to search for")
@click.option("-i", "--institute", help="institute id of related cases")
@click.option("-r", "--reruns", is_flag=True, help="requested to be rerun")
@click.option("-f", "--finished", is_flag=True, help="archived or solved")
@click.option("--causatives", is_flag=True, help="Has causative variants")
@click.option("--research-requested", is_flag=True, help="If research is requested")
@click.option("--is-research", is_flag=True, help="If case is in research mode")
@click.option(
    "-s",
    "--status",
    type=click.Choice(CASE_STATUSES),
    help="Specify what status to look for",
)
@click.option("--within-days", type=int, help="Days since event related to case")
@json_option
@with_appcontext
def cases(
    case_id,
    institute,
    reruns,
    finished,
    causatives,
    research_requested,
    is_research,
    status,
    within_days,
    json,
):
    """Interact with cases existing in the database."""
    adapter = store

    models = []
    if case_id:
        case_obj = adapter.case(case_id=case_id)
        if case_obj:
            models.append(case_obj)
        else:
            LOG.info("No case with id {}".format(case_id))

    else:
        models = adapter.cases(
            collaborator=institute,
            reruns=reruns,
            finished=finished,
            has_causatives=causatives,
            research_requested=research_requested,
            is_research=is_research,
            status=status,
            within_days=within_days,
        )
        models = [case_obj for case_obj in models]
        if len(models) == 0:
            LOG.info("No cases could be found")

    if json:
        click.echo(json_lib.dumps(models, default=bson_handler))
        return

    for model in models:
        pp(model)
