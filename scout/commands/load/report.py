"""Code for updating reports"""
import logging

import click
from flask.cli import with_appcontext

from scout.constants import CUSTOM_CASE_REPORTS
from scout.load.report import update_case_report

LOG = logging.getLogger(__name__)


####### The following commands are deprecated and will be removed in Scout release >= 5.0 #######
@click.command("delivery-report", deprecated=True)
@click.argument("case_id")
@click.argument("report_path", type=click.Path(exists=True))
@click.option("-update", "--update", is_flag=True, help="update delivery report for a sample")
@with_appcontext
def delivery_report(case_id, report_path, update):
    """Add delivery report to an existing case."""
    try:
        update_case_report(case_id, report_path, "delivery")
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()


@click.command("cnv-report", deprecated=True)
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=True)
@click.option("-u", "--update", is_flag=True, help="update CNV report for a sample")
@with_appcontext
def cnv_report(case_id, report_path, update):
    """Add CNV report report to an existing case."""

    try:
        update_case_report(case_id, report_path, "cnv")
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()


@click.command("coverage-qc-report", deprecated=True)
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=True)
@click.option("-u", "--update", is_flag=True, help="update coverage and qc report for a sample")
@with_appcontext
def coverage_qc_report(case_id, report_path, update):
    """Add coverage and qc report to an existing case."""

    try:
        update_case_report(case_id, report_path, "cov_qc")
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()


@click.command("gene-fusion-report", deprecated=True)
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=True)
@click.option("-r", "--research", is_flag=True, help="Update research gene fusion report")
@click.option("-u", "--update", is_flag=True, help="Update a gene fusion report for a case")
@with_appcontext
def gene_fusion_report(case_id, report_path, research, update):
    """Add or update a gene fusion report (clinical or research) for a case."""

    try:
        if research:
            update_case_report(case_id, report_path, "gene_fusion_research")
        else:
            update_case_report(case_id, report_path, "gene_fusion")

        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()


####### End of deprecated commands #######


@click.command("report")
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=True)
@click.option(
    "-t",
    "--report-type",
    type=click.Choice(list(CUSTOM_CASE_REPORTS.keys())),
    required=True,
    help="Type of report",
)
@with_appcontext
def report(case_id, report_path, report_type):
    """Load a report document for a case."""
    updated_case = update_case_report(case_id, report_path, report_type)
    if updated_case:
        LOG.info(f"Report '{report_type}' updated for case {case_id}")
    else:
        LOG.warning(f"Could not update report '{report_type}' for case {case_id}")
