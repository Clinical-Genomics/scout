# -*- coding: utf-8 -*-
from functools import partial
import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command(short_help="Upload research variants")
@click.option("-c", "--case-id", help="family or case id")
@click.option("-i", "--institute", help="institute id of related cases")
@click.option("-f", "--force", is_flag=True, help="upload without request")
@with_appcontext
def research(case_id, institute, force):
    """Upload research variants to cases

    If a case is specified, all variants found for that case will be
    uploaded.

    If no cases are specified then all cases that have 'research_requested'
    will have there research variants uploaded
    """
    LOG.info("Running scout load research")
    adapter = store

    if case_id:
        if not institute:
            # There was an old way to create case ids so we need a special case to handle this
            # Assume institute-case combo
            splitted_case = case_id.split("-")
            # Check if first part is institute, then we know it is the old format
            if len(splitted_case) > 1:
                institute_obj = adapter.institute(splitted_case[0])
                if institute_obj:
                    institute = institute_obj["_id"]
                    case_id = splitted_case[1]
        case_obj = adapter.case(institute_id=institute, case_id=case_id)
        if case_obj is None:
            LOG.warning("No matching case found")
            raise click.Abort()
        case_objs = [case_obj]
    else:
        # Fetch all cases that have requested research
        case_objs = adapter.cases(research_requested=True)

    default_threshold = 8
    files = False
    for case_obj in case_objs:
        if force or case_obj["research_requested"]:
            # Test to upload research snvs
            if case_obj["vcf_files"].get("vcf_snv_research"):
                files = True
                adapter.delete_variants(
                    case_id=case_obj["_id"], variant_type="research", category="snv"
                )

                LOG.info("Load research SNV for: %s", case_obj["_id"])
                adapter.load_variants(
                    case_obj=case_obj,
                    variant_type="research",
                    category="snv",
                    rank_threshold=default_threshold,
                )

            # Test to upload research svs
            if case_obj["vcf_files"].get("vcf_sv_research"):
                files = True
                adapter.delete_variants(
                    case_id=case_obj["_id"], variant_type="research", category="sv"
                )
                LOG.info("Load research SV for: %s", case_obj["_id"])
                adapter.load_variants(
                    case_obj=case_obj,
                    variant_type="research",
                    category="sv",
                    rank_threshold=default_threshold,
                )

            # Test to upload research cancer variants
            if case_obj["vcf_files"].get("vcf_cancer_research"):
                files = True
                adapter.delete_variants(
                    case_id=case_obj["_id"], variant_type="research", category="cancer"
                )

                LOG.info("Load research cancer for: %s", case_obj["_id"])
                adapter.load_variants(
                    case_obj=case_obj,
                    variant_type="research",
                    category="cancer",
                    rank_threshold=default_threshold,
                )
            if not files:
                LOG.warning("No research files found for case %s", case_id)
                raise click.Abort()
            case_obj["is_research"] = True
            case_obj["research_requested"] = False
            adapter.update_case(case_obj, keep_date=True)
        else:
            LOG.warning("research not requested, use '--force'")
