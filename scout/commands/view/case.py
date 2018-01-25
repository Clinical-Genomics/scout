import logging

from pprint import pprint as pp

import click

from scout.constants import CASE_STATUSES

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
@click.pass_context
def cases(context, case_id, institute, reruns, finished, causatives, research_requested,
          is_research, status):
    """Interact with cases existing in the database."""
    adapter = context.obj['adapter']

    models = []
    if case_id:
        case_obj = adapter.case(case_id=case_id)
        if case_obj:
            models.append(case_obj)

    else:
        models = adapter.cases(collaborator=institute, reruns=reruns,
                           finished=finished, has_causatives=causatives,
                           research_requested=research_requested,
                           is_research=is_research, status=status)
    i = 0
    for model in models:
        i += 1
        pp(model)
    
    if i == 0:
        LOG.info("No cases could be found")

