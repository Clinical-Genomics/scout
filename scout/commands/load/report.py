import logging
import click

from scout.load.report import load_delivery_report

LOG = logging.getLogger(__name__)


@click.command()
@click.argument('case_id', required=False)
@click.argument('institute_id', required=False)
@click.argument('display_name', required=False)
@click.argument('analysis_date')
@click.argument('report_path', type=click.Path(exists=True))
@click.argument('update', required=False)
@click.pass_context
def delivery_report(context, case_id, institute_id, display_name, analysis_date, report_path,
                    update):
    """Add delivery report to an existing case."""

    adapter = context.obj['adapter']

    try:
        load_delivery_report(adapter, case_id, institute_id, display_name, analysis_date,
                             report_path, update)
        LOG.info("saved report to case!")
    except Exception as e:
        LOG.error(e)
        context.abort()
