"""Code for updating reports"""

import logging

import click
from flask.cli import with_appcontext

from scout.constants import CUSTOM_CASE_REPORTS
from scout.update.report import update_case_report

LOG = logging.getLogger(__name__)


@click.command("report")
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=False)
@click.option("--delete", "-d", is_flag=True, help="Delete the given report from the case.")
@click.option(
    "-t",
    "--report-type",
    type=click.Choice(list(CUSTOM_CASE_REPORTS.keys())),
    required=True,
    help="Type of report",
)
@with_appcontext
def report(case_id, report_path, report_type, delete):
    """Update (or delete) a report document for a case."""

    if not delete and not report_path:
        LOG.error(
            "Please provide a path to the report to update, or the --delete flag to remove the report type."
        )
        raise click.Abort()

    updated_case = update_case_report(case_id, report_path, report_type, delete)
    if updated_case:
        LOG.info(f"Report '{report_type}' updated for case {case_id}")
    else:
        LOG.warning(f"Could not update report '{report_type}' for case {case_id}")
