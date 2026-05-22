import datetime
import json as json_lib
import logging
import os
from typing import Any, Dict, Optional, Tuple

import click
from flask.cli import with_appcontext
from xlsxwriter import Workbook

from scout.constants import CALLERS, DATE_DAY_FORMATTER
from scout.constants.managed_variant import MANAGED_CATEGORIES
from scout.constants.variants_export import VERIFIED_VARIANTS_HEADER
from scout.export.variant import (
    export_managed_variants,
    export_verified_variants,
)
from scout.server.blueprints.institutes.controllers import variants_to_managed_variants
from scout.server.extensions import store
from scout.utils.vcf import build_vcf_header, print_vcf, validate_vcf_line

from .export_handler import bson_handler
from .utils import build_option, category_option, collaborator_option, json_option

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
    "--category",
    type=click.Choice(MANAGED_CATEGORIES, case_sensitive=False),
    multiple=True,
    default=MANAGED_CATEGORIES,
    show_default=True,
    help="One or more categories to include.",
)
@collaborator_option
@build_option
@json_option
@click.option(
    "--liftover-from",
    type=click.Choice(BUILDS),
    help="Perform liftover on coordinates and export as managed variants infile.",
)
@with_appcontext
def managed(collaborator: str, category: Tuple[str], build: str, json: bool, liftover_from: Optional[str]):
    """Export managed variants for a collaborator in VCF or JSON format"""
    LOG.info("Running scout export managed variants")
    adapter = store

    genome_build = build
    if build == "GRCh38":
        genome_build = "38"

    variants = export_managed_variants(
        adapter=adapter, institute=collaborator, build=genome_build, category=list(category)
    )

    if json:
        click.echo(json_lib.dumps([var for var in variants], default=bson_handler))
        return

    print_vcf(variants=variants, build=build, export_category="MANAGED", liftover_from=liftover_from)


def resolve_case(
    adapter: Any,
    case_id: Optional[str],
    collaborator: str,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Resolve the effective collaborator and optional case object.

    If case_id is provided, the case is fetched and its owner is used
    as the collaborator. If the case does not exist, the command aborts.

    Returns:
        Tuple of (collaborator, case object or None)
    """
    if not case_id:
        LOG.info("Use collaborator %s", collaborator)
        return collaborator, None

    case_obj = adapter.case(case_id)
    if not case_obj:
        LOG.info("Case %s does not exist", case_id)
        raise click.Abort

    return case_obj["owner"], case_obj


@click.command("causatives", short_help="Export causative variants")
@build_option
@category_option
@collaborator_option
@click.option("-d", "--document-id", help="Search for a specific variant")
@click.option("--case-id", help="Find causative variants for case")
@json_option
@click.option("--as-managed", is_flag=True, help="Export to managed variants infile")
@click.option(
    "--managed-link-base-url",
    help="Export to managed variants infile, with full link to the variant",
)
@click.option("--within-days", type=int, help="Days since mark causative event occurred")
@with_appcontext
def causatives(
    build: str,
    collaborator: str,
    category: str,
    document_id: str | None,
    case_id: str | None,
    json: bool,
    as_managed: bool,
    managed_link_base_url: str | None,
    within_days: int | None,
):
    """
    Export causative variants. You can select causatives on variant document id or case id or search by collaborator, category or variant age.

    Supports multiple output formats:
    - JSON (--json)
    - Managed variants infile (--as-managed with --managed-link-base-url)
    - VCF (default)

    Data can be queried by:
    - collaborator (institute)
    - case ID (optional; overrides collaborator owner if provided)
    - document ID
    - category
    - variant age (--within-days)

    If a case ID is provided, its owner is used as the collaborator.
    For GRCh38 builds, variants are queried using build "38" and then printed with prefix "chr".
    """
    LOG.info("Running scout export variants")
    adapter = store

    collaborator, case_obj = resolve_case(adapter, case_id, collaborator)

    build = "38" if build == "GRCh38" else build

    causatives = adapter.get_causatives(
        document_id=document_id,
        institute_id=collaborator,
        case_id=case_id,
        build=build,
        category=category,
        within_days=within_days,
    )

    if json:
        click.echo(json_lib.dumps(list(causatives), default=bson_handler))
        return

    if as_managed:
        if not managed_link_base_url:
            LOG.info("Please provide a value for --managed-link-base-url")
            raise click.Abort
        for line in variants_to_managed_variants(
            variants=causatives, type="causatives", base_url=managed_link_base_url
        ):
            click.echo(line)
        return

    print_vcf(variants=causatives, build=build, export_category="CAUSATIVE", case_obj=case_obj)