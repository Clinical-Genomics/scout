# -*- coding: utf-8 -*-
import logging
import tempfile
from contextlib import contextmanager
from os import path
from typing import Iterator, Optional, TextIO

import click
import yaml
from flask import current_app
from flask.cli import with_appcontext

from scout.adapter import MongoAdapter
from scout.constants import ORDERED_FILE_TYPE_MAP
from scout.server.extensions import store

DEFAULT_RANK_THRESHOLD = 8
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

    adapter.load_variants(
        case_obj=case_obj,
        variant_type=variant_type,
        category=category,
        rank_threshold=rank_treshold,
        build=case_obj["genome_build"],
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


@contextmanager
def temp_case_config_from_case_dict(case_obj: dict) -> Iterator[TextIO]:
    """Create a temporary case config YAML file from a case dictionary."""
    case_config = {
        "family": case_obj["_id"],
        "owner": case_obj["owner"],
        "human_genome_build": case_obj["genome_build"],
        "rank_score_threshold": int(case_obj["rank_score_threshold"]),
        "samples": [
            {
                "sample_id": individual["individual_id"],
            }
            for individual in case_obj.get("individuals", [])
        ],
        "gene_panels": [panel["panel_name"] for panel in case_obj.get("panels", [])],
    }

    research_vcf_fields = [
        "vcf_snv_research",
        "vcf_sv_research",
        "vcf_snv_research_mt",
        "vcf_sv_research_mt",
        "vcf_mei_research",
        "vcf_cancer_research",
        "vcf_cancer_sv_research",
        "vcf_fusion_research",
    ]

    vcf_files = case_obj.get("vcf_files", {})

    case_config.update({key: vcf_files[key] for key in research_vcf_fields if key in vcf_files})

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yaml",
        encoding="utf-8",
    ) as yaml_file:
        yaml.safe_dump(case_config, yaml_file, sort_keys=False)
        yaml_file.flush()
        yield yaml_file


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
        case_objs = adapter.cases(research_requested=True)

    raise_file_not_found = False
    missing_per_case = {}

    external_variants_loader = current_app.config.get("VARIANTS_LOADER")

    for case_obj in case_objs:
        if not (force or case_obj["research_requested"]):
            LOG.warning("research not requested, use '--force'")
            continue

        if external_variants_loader:
            with temp_case_config_from_case_dict(case_obj=case_obj) as yaml_file:
                adapter.run_scout_loader(case_config=yaml_file, research=True)
                continue

        files = False

        for file_type in ORDERED_FILE_TYPE_MAP:
            if ORDERED_FILE_TYPE_MAP[file_type]["variant_type"] != "research":
                continue

            file_path = case_obj["vcf_files"].get(file_type)

            if file_path:
                if not path.isfile(file_path):
                    raise_file_not_found = True
                    missing_per_case.setdefault(case_obj["_id"], []).append(file_path)
                    continue

                files = True
                upload_research_variants(
                    adapter=adapter,
                    case_obj=case_obj,
                    variant_type="research",
                    category=ORDERED_FILE_TYPE_MAP[file_type]["category"],
                    rank_treshold=case_obj.get("rank_score_threshold", DEFAULT_RANK_THRESHOLD),
                )

        if not files:
            continue

        case_obj["is_research"] = True
        case_obj["research_requested"] = False
        adapter.update_case(case_obj, keep_date=True)

        adapter.case_variants_count(
            case_obj["_id"], case_obj["owner"], "research", force_update_case=True
        )

    if raise_file_not_found:
        message = "\n\n".join(
            f"Case {case_id}: missing {', '.join(files)}"
            for case_id, files in missing_per_case.items()
        )
        raise FileNotFoundError(f"Some cases are missing research files:\n{message}")
