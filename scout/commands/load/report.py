import logging

import click

from .case import case as case_command

from .institute import institute as institute_command
from .panel import panel as panel_command
from .research import research as research_command
from .variants import variants as variants_command
from .region import region as region_command
from .user import user as user_command

LOG = logging.getLogger(__name__)



@load.command()
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
