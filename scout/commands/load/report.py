"""Code for updating delivery reports"""
import logging

import click
from flask.cli import with_appcontext

from scout.load.report import load_delivery_report
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("delivery-report")
@click.argument("case_id")
@click.argument("report_path", type=click.Path(exists=True))
@click.option(
    "-update", "--update", is_flag=True, help="update delivery report for a sample"
)
@with_appcontext
def delivery_report(case_id, report_path, update):
    """Add delivery report to an existing case."""

    adapter = store

    try:
        load_delivery_report(
            adapter=adapter, case_id=case_id, report_path=report_path, update=update
        )
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
