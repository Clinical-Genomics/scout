import logging
import click

LOG = logging.getLogger(__name__)


@click.command('institutes', short_help='Display institutes')
@click.pass_context
def institutes(context):
    """Show all institutes in the database"""
    LOG.info("Running scout view institutes")
    adapter = context.obj['adapter']

    institute_objs = adapter.institutes()
    if institute_objs.count() == 0:
        click.echo("No institutes found")
        context.abort()

    click.echo("#institute_id\tdisplay_name")
    for institute_obj in institute_objs:
        click.echo("{0}\t{1}".format(
            institute_obj['_id'],
            institute_obj['display_name']
        ))
