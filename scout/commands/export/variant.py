import datetime
import json as json_lib
import logging
import os

import click
from flask.cli import with_appcontext
from xlsxwriter import Workbook

from scout.constants import CALLERS, DATE_DAY_FORMATTER
from scout.constants.variants_export import VCF_HEADER, VERIFIED_VARIANTS_HEADER
from scout.export.variant import export_managed_variants, export_variants, export_verified_variants
from scout.server.extensions import store

from .export_handler import bson_handler
from .utils import build_option, json_option

LOG = logging.getLogger(__name__)


@click.command("verified", short_help="Export validated variants")
@click.option(
    "-c",
    "--collaborator",
    help="Specify what collaborator to export variants from. Defaults to cust000",
)
@click.option("--outpath", help="Path to output file")
@click.option("--test", help="Use this flag to test the function", is_flag=True)
@with_appcontext
def verified(collaborator, test, outpath=None):
    """Export variants which have been verified for an institute
        and write them to an excel file.

    Args:
        collaborator(str): institute id
        test(bool): True if the function is called for testing purposes
        outpath(str): path to output file

    Returns:
        written_files(int): number of written or simulated files
    """
    written_files = 0
    collaborator = collaborator or "cust000"
    LOG.info("Exporting verified variants for cust {}".format(collaborator))

    adapter = store
    verified_vars = adapter.verified(institute_id=collaborator)
    LOG.info("FOUND {} verified variants for institute {}".format(len(verified_vars), collaborator))

    if not verified_vars:
        LOG.warning(
            "There are no verified variants for institute {} in database!".format(collaborator)
        )
        return None

    unique_callers = set()
    for var_type, var_callers in CALLERS.items():
        for caller in var_callers:
            unique_callers.add(caller.get("id"))

    document_lines = export_verified_variants(verified_vars, unique_callers)

    today = datetime.datetime.now().strftime(DATE_DAY_FORMATTER)
    document_name = ".".join(["verified_variants", collaborator, today]) + ".xlsx"

    # If this was a test and lines are created return success
    if test and document_lines:
        written_files += 1
        LOG.info("Success. Verified variants file contains {} lines".format(len(document_lines)))
        return written_files
    if test:
        LOG.info(
            "Could not create document lines. Verified variants not found for customer {}".format(
                collaborator
            )
        )
        return

    # create workbook and new sheet
    # set up outfolder
    if not outpath:
        outpath = str(os.getcwd())
    workbook = Workbook(os.path.join(outpath, document_name))
    Report_Sheet = workbook.add_worksheet()

    # Write the column header
    row = 0
    for col, field in enumerate(VERIFIED_VARIANTS_HEADER):
        Report_Sheet.write(row, col, field)

    # Write variant lines, after header (start at line 1)
    for row, line in enumerate(document_lines, 1):  # each line becomes a row in the document
        for col, field in enumerate(line):  # each field in line becomes a cell
            Report_Sheet.write(row, col, field)
    workbook.close()

    if os.path.exists(os.path.join(outpath, document_name)):
        LOG.info(
            "Success. Verified variants file of {} lines was written to disk".format(
                len(document_lines)
            )
        )
        written_files += 1

    return written_files


@click.command("managed", short_help="Export managed variants")
@click.option(
    "-c",
    "--collaborator",
    help="Specify what collaborator to export variants from. Defaults to all variants.",
)
@build_option
@json_option
@with_appcontext
def managed(collaborator: str, build: str, json: bool):
    """Export managed variants for a collaborator in VCF or JSON format"""
    LOG.info("Running scout export managed variants")
    adapter = store

    variants = export_managed_variants(adapter, collaborator, build)

    if json:
        click.echo(json_lib.dumps([var for var in variants], default=bson_handler))
        return

    vcf_header = VCF_HEADER
    vcf_header.insert(2, "##fileDate={}".format(datetime.datetime.now()))

    for line in vcf_header:
        click.echo(line)

    for variant_obj in variants:
        variant_string = get_vcf_entry(variant_obj)
        click.echo(variant_string)


@click.command("variants", short_help="Export variants")
@click.option(
    "-c",
    "--collaborator",
    help="Specify what collaborator to export variants from. Defaults to cust000",
)
@click.option("-d", "--document-id", help="Search for a specific variant")
@click.option("--case-id", help="Find causative variants for case")
@json_option
@with_appcontext
def variants(collaborator: str, document_id: str, case_id: str, json: bool):
    """Export causatives for a collaborator in .vcf format"""
    LOG.info("Running scout export variants")
    adapter = store
    collaborator = collaborator or "cust000"
    LOG.info("Use collaborator %s", collaborator)
    if case_id:
        case_obj = adapter.case(case_id)
        if not case_obj:
            LOG.info("Case %s does not exist", case_id)
            raise click.Abort

    variants = export_variants(adapter, collaborator, document_id=document_id, case_id=case_id)

    if json:
        click.echo(json_lib.dumps([var for var in variants], default=bson_handler))
        return

    vcf_header = VCF_HEADER

    # If case_id is given, print more complete vcf entries, with INFO,
    # and genotypes
    if case_id:
        vcf_header[-1] = vcf_header[-1] + "\tFORMAT"
        case_obj = adapter.case(case_id=case_id)
        for individual in case_obj["individuals"]:
            vcf_header[-1] = vcf_header[-1] + "\t" + individual["individual_id"]

    for line in vcf_header:
        click.echo(line)

    for variant_obj in variants:
        variant_string = get_vcf_entry(variant_obj, case_id=case_id)
        click.echo(variant_string)


def get_vcf_entry(variant_obj, case_id=None):
    """
    Get vcf entry from variant object

    Args:
        variant_obj(dict)
    Returns:
        variant_string(str): string representing variant in vcf format
    """
    if variant_obj["category"] == "snv":
        var_type = "TYPE"
    else:
        var_type = "SVTYPE"

    info_field = ";".join(
        [
            "END=" + str(variant_obj["end"]),
            var_type + "=" + variant_obj["sub_category"].upper(),
        ]
    )

    variant_string = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}".format(
        variant_obj["chromosome"],
        variant_obj["position"],
        variant_obj.get("dbsnp_id", "."),
        variant_obj["reference"],
        variant_obj["alternative"],
        variant_obj.get("quality", "."),
        ";".join(variant_obj.get("filters", [])),
        info_field,
    )

    if case_id:
        variant_string += "\tGT"
        for sample in variant_obj["samples"]:
            variant_string += "\t" + sample["genotype_call"]

    return variant_string
