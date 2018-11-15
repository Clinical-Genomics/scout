import logging
import json


from pprint import pprint as pp

from bson.json_util import dumps

import click

from scout.constants import CASE_STATUSES
from .utils import json_option

LOG = logging.getLogger(__name__)

@click.command('cases', short_help='Fetch cases')
@click.option('--case-id',
              help='Case id to search for'
)
@click.option('-i', '--institute',
              help='institute id of related cases'
)
@click.option('-r', '--reruns',
              is_flag=True,
              help='requested to be rerun'
)
@click.option('-f', '--finished',
              is_flag=True,
              help='archived or solved'
)
@click.option('--causatives',
              is_flag=True,
              help='Has causative variants'
)
@click.option('--research-requested',
              is_flag=True,
              help='If research is requested'
)
@click.option('--is-research',
              is_flag=True,
              help='If case is in research mode'
)
@click.option('-s', '--status',
              type=click.Choice(CASE_STATUSES),
              help='Specify what status to look for'
)
@json_option
@click.pass_context
def cases(context, case_id, institute, reruns, finished, causatives, research_requested,
          is_research, status, json):
    """Interact with cases existing in the database."""
    adapter = context.obj['adapter']

    models = []
    if case_id:
        case_obj = adapter.case(case_id=case_id)
        if case_obj:
            models.append(case_obj)
        else:
            LOG.info("No case with id {}".format(case_id))

    else:
        models = adapter.cases(collaborator=institute, reruns=reruns,
                           finished=finished, has_causatives=causatives,
                           research_requested=research_requested,
                           is_research=is_research, status=status)
        models = [case_obj for case_obj in models]
        if len(models) == 0:
            LOG.info("No cases could be found")

    if json:
        click.echo(dumps(models))
        return

    for model in models:
        pp(model)
