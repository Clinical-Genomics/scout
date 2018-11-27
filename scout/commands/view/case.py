import logging
import click

LOG = logging.getLogger(__name__)


@click.command('cases', short_help='Display cases')
@click.option('-i', '--institute',
    help="What institute to show cases from"
)
@click.option('-d', '--display-name',
    help="Search with display name"
)
@click.option('-c', '--case-id',
    help="Search for a specific case"
)
@click.pass_context
def cases(context, institute, display_name, case_id):
    """Display cases from the database"""
    LOG.info("Running scout view institutes")
    adapter = context.obj['adapter']

    models = []
    if case_id:
        case_obj = adapter.case(case_id=case_id)
        if case_obj:
            models.append(case_obj)

    else:
        models = adapter.cases(collaborator=institute, name_query=display_name)
        models = [case_obj for case_obj in models]

    if not models:
        LOG.info("No cases could be found")
        return

    click.echo("#case_id\tdisplay_name\tinstitute")
    for model in models:
        click.echo("{0}\t{1}\t{2}".format(
            model['_id'],
            model['display_name'],
            model['owner'],
        ))
