import logging
import click

from scout.load.report import load_report
from scout.exceptions import (IntegrityError, ValidationError)

LOG = logging.getLogger(__name__)

@click.command()
@click.argument('case_id')
@click.argument('report_path', type=click.Path(exists=True))
@click.option('-u', '--update', 
    is_flag=True
)
@click.pass_context
def report(context, case_id, report_path, update):
    """Add delivery report to an existing case."""
    adapter = context.obj['adapter']
    try:
        updated_case = load_report(adapter, case_id, report_path, update)
    except IntegrityError as err:
        LOG.warning(err)
        context.abort()
    except ValidationError as err:
        LOG.warning(err)
        LOG.info("Use flag --update if it should be overwritten")
        context.abort()
