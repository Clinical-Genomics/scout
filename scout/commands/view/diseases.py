import logging
import click

LOG = logging.getLogger(__name__)


@click.command('diseases', short_help='Display all diseases')
@click.pass_context
def diseases(context):
    """Show all diseases in the database"""
    LOG.info("Running scout view diseases")
    adapter = context.obj['adapter']

    disease_objs = adapter.disease_terms()

    nr_diseases = disease_objs.count()
    if nr_diseases == 0:
        click.echo("No diseases found")
    else:
        click.echo("Disease")
        for disease_obj in adapter.disease_terms():
            click.echo("{0}".format(disease_obj['_id']))
        LOG.info("{0} diseases found".format(nr_diseases))
