import logging
import click

LOG = logging.getLogger(__name__)


@click.command('hpo', short_help='Display all hpo terms')
@click.pass_context
def hpo(context):
    """Show all hpo terms in the database"""
    LOG.info("Running scout view hpo")
    adapter = context.obj['adapter']

    click.echo("hpo_id\tdescription")
    for hpo_obj in adapter.hpo_terms():
        click.echo("{0}\t{1}".format(
            hpo_obj['hpo_id'],
            hpo_obj['description'],
        ))
