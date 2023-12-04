# -*- coding: utf-8 -*-
import logging
from os import path
from typing import Optional

import click
from flask.cli import with_appcontext

from scout.adapter import MongoAdapter
from scout.constants import FILE_TYPE_MAP
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def upload_research_variants(
    adapter: MongoAdapter,
    case_obj: dict,
    variant_type: str,
    category: str,
    rank_treshold: int,
):
    """Delete existing variants and upload new variants"""
    adapter.delete_variants(case_id=case_obj["_id"], variant_type=variant_type, category=category)

    LOG.info("Load %s %s for: %s", variant_type, category.upper(), case_obj["_id"])
    adapter.load_variants(
        case_obj=case_obj,
        variant_type=variant_type,
        category=category,
        rank_threshold=rank_treshold,
    )


def get_case_and_institute(
    adapter: MongoAdapter, case_id: str, institute: Optional[str]
) -> (str, str):
    """Fetch the case_id and institute_id

    There was an old way to create case ids so we need a special case to handle this.
    For old case_id we assume institute-case combo
    We check if first part of the case_id is institute, then we know it is the old format
    """
    if institute:
        return case_id, institute
    split_case = case_id.split("-")
    institute_id = None

    if len(split_case) > 1:
        institute_id = split_case[0]
        institute_obj = adapter.institute(institute_id)
        if institute_obj:
            institute_id = institute_obj["_id"]
            case_id = split_case[1]
    return case_id, institute_id


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
        case_id, institute_id = get_case_and_institute(
            adapter=adapter, case_id=case_id, institute=institute
        )
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
    raise_file_not_found = False
    for case_obj in case_objs:
        if not (force or case_obj["research_requested"]):
            LOG.warning("research not requested, use '--force'")
            continue

        for file_type in FILE_TYPE_MAP:
            if FILE_TYPE_MAP[file_type]["variant_type"] != "research":
                continue

            if case_obj["vcf_files"].get(file_type):
                if not path.isfile(case_obj["vcf_files"].get(file_type)):
                    raise_file_not_found = True
                    continue
                files = True
                upload_research_variants(
                    adapter=adapter,
                    case_obj=case_obj,
                    variant_type="research",
                    category=FILE_TYPE_MAP[file_type]["category"],
                    rank_treshold=default_threshold,
                )

        if not files:
            LOG.warning(
                "Research requested, but no research files found for case %s. Consider ordering a rerun.",
                case_obj["_id"],
            )
            raise_file_not_found = True
            continue
        case_obj["is_research"] = True
        case_obj["research_requested"] = False
        adapter.update_case(case_obj, keep_date=True)

        # Update case variants count
        adapter.case_variants_count(
            case_obj["_id"], case_obj["owner"], "research", force_update_case=True
        )

    if raise_file_not_found:
        raise FileNotFoundError(
            "At least one of the remaining cases where research is requested is missing all research files."
        )
