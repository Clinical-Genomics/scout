"""Code for updating reports"""
import logging

import click
from flask.cli import with_appcontext

from scout.load.report import load_delivery_report, load_cnv_report, load_coverage_qc_report
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("delivery-report")
@click.argument("case_id")
@click.argument("report_path", type=click.Path(exists=True))
@click.option("-update", "--update", is_flag=True, help="update delivery report for a sample")
@with_appcontext
def delivery_report(case_id, report_path, update):
    """Add delivery report to an existing case."""

    adapter = store

    try:
        load_delivery_report(
            adapter=adapter,
            case_id=case_id,
            report_path=report_path,
            update=update,
        )
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()


@click.command("cnv-report")
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=True)
@click.option("-u", "--update", is_flag=True, help="update CNV report for a sample")
@with_appcontext
def cnv_report(case_id, report_path, update):
    """Add CNV report report to an existing case."""

    adapter = store

    try:
        load_cnv_report(
            adapter=adapter,
            case_id=case_id,
            report_path=report_path,
            update=update,
        )
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()


@click.command("coverage-qc-report")
@click.argument("case-id", required=True)
@click.argument("report-path", type=click.Path(exists=True), required=True)
@click.option("-u", "--update", is_flag=True, help="update coverage and qc report for a sample")
@with_appcontext
def coverage_qc_report(case_id, report_path, update):
    """Add coverage and qc report to an existing case."""

    adapter = store

    try:
        load_coverage_qc_report(
            adapter=adapter,
            case_id=case_id,
            report_path=report_path,
            update=update,
        )
        LOG.info("saved report to case!")
    except Exception as err:
        LOG.error(err)
        raise click.Abort()
