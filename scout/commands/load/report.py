import logging
import click

from scout.load.report import load_delivery_report

LOG = logging.getLogger(__name__)


@click.command('delivery-report')
@click.argument('case_id')
@click.argument('report_path', type=click.Path(exists=True))
@click.option('-update', '--update', is_flag=True, help='update delivery report for a sample')
@click.pass_context
def delivery_report(context, case_id, report_path,
                    update):
    """Add delivery report to an existing case."""

    adapter = context.obj['adapter']

    try:
        load_delivery_report(adapter=adapter, case_id=case_id,
                             report_path=report_path, update=update)
        LOG.info("saved report to case!")
    except Exception as e:
        LOG.error(e)
        context.abort()
