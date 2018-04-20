import logging
import click

LOG = logging.getLogger(__name__)


@click.command('panels', short_help='Display gene panels')
@click.option('-i', '--institute',
              help='institute id'
              )
@click.pass_context
def panels(context, institute):
    """Show all gene panels in the database"""
    LOG.info("Running scout view panels")
    adapter = context.obj['adapter']

    panel_objs = adapter.gene_panels(institute_id=institute)
    if panel_objs.count() == 0:
        LOG.info("No panels found")
        context.abort()
    click.echo("#panel_name\tversion\tnr_genes\tdate")

    for panel_obj in panel_objs:
        click.echo("{0}\t{1}\t{2}\t{3}".format(
            panel_obj['panel_name'],
            str(panel_obj['version']),
            len(panel_obj['genes']),
            str(panel_obj['date'].strftime('%Y-%m-%d'))
        ))

