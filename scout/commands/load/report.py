import logging
import click

LOG = logging.getLogger(__name__)


@click.command()
@click.argument('case_id')
@click.argument('report_path', type=click.Path(exists=True))
@click.pass_context
def report(context, case_id, report_path):
    """Add delivery report to an existing case."""
    adapter = context.obj['adapter']
    customer, family = case_id.split('-', 1)
    existing_case = adapter.case(customer, family)
    if existing_case is None:
        LOG.warning("no case found")
        context.abort()
    existing_case.delivery_report = report_path
    existing_case.save()
    LOG.info("saved report to case!")
