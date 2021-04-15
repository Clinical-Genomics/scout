#!/usr/bin/env python
# encoding: utf-8
"""
update_cases.py

Update cases with information from a old instance

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""
import logging

import click
import ruamel.yaml
from pymongo import MongoClient
from pymongo.database import Database

from scout.adapter import MongoAdapter
from scout.adapter.mongo.case import get_variantid

LOG = logging.getLogger(__name__)


def archive_info(database: Database, archive_case: dict) -> dict:
    """Get information about a case from archive."""
    data = {
        "collaborators": archive_case["collaborators"],
        "synopsis": archive_case.get("synopsis"),
        "assignees": [],
        "suspects": [],
        "causatives": [],
        "phenotype_terms": [],
        "phenotype_groups": [],
    }
    if archive_case.get("assignee"):
        archive_user = database.user.find_one({"_id": archive_case["assignee"]})
        data["assignee"].append(archive_user["email"])

    for key in ["suspects", "causatives"]:
        for variant_id in archive_case.get(key, []):
            archive_variant = database.variant.find_one({"_id": variant_id})
            data[key].append(
                {
                    "chromosome": archive_variant["chromosome"],
                    "position": archive_variant["position"],
                    "reference": archive_variant["reference"],
                    "alternative": archive_variant["alternative"],
                    "variant_type": archive_variant["variant_type"],
                }
            )

    for key in ["phenotype_terms", "phenotype_groups"]:
        for archive_term in archive_case.get(key, []):
            data[key].append(
                {
                    "phenotype_id": archive_term["phenotype_id"],
                    "feature": archive_term["feature"],
                }
            )

    return data


def migrate_case(adapter: MongoAdapter, scout_case: dict, archive_data: dict):
    """Migrate case information from archive."""
    # update collaborators
    collaborators = list(set(scout_case["collaborators"] + archive_data["collaborators"]))
    if collaborators != scout_case["collaborators"]:
        LOG.info(f"set collaborators: {', '.join(collaborators)}")
        scout_case["collaborators"] = collaborators

    # update assignees
    if len(scout_case.get("assignees", [])) == 0:
        scout_user = adapter.user(archive_data["assignee"])
        if scout_user:
            scout_case["assignees"] = [archive_data["assignee"]]
        else:
            LOG.warning(f"{archive_data['assignee']}: unable to find assigned user")

    # add/update suspected/causative variants
    for key in ["suspects", "causatives"]:
        scout_case[key] = scout_case.get(key, [])
        for archive_variant in archive_data[key]:
            variant_id = get_variantid(archive_variant, scout_case["_id"])
            scout_variant = adapter.variant(variant_id)
            if scout_variant:
                if scout_variant["_id"] in scout_case[key]:
                    LOG.info(f"{scout_variant['_id']}: variant already in {key}")
                else:
                    LOG.info(f"{scout_variant['_id']}: add to {key}")
                    scout_variant[key].append(scout_variant["_id"])
            else:
                LOG.warning(f"{scout_variant['_id']}: unable to find variant ({key})")
                scout_variant[key].append(variant_id)

    if not scout_case.get("synopsis"):
        # update synopsis
        scout_case["synopsis"] = archive_data["synopsis"]

    scout_case["is_migrated"] = True
    adapter.case_collection.find_one_and_replace({"_id": scout_case["_id"]}, scout_case)

    # add/update phenotype groups/terms
    scout_institute = adapter.institute(scout_case["owner"])
    scout_user = adapter.user("mans.magnusson@scilifelab.se")
    for key in ["phenotype_terms", "phenotype_groups"]:
        for archive_term in archive_data[key]:
            adapter.add_phenotype(
                institute=scout_institute,
                case=scout_case,
                user=scout_user,
                link=f"/{scout_case['owner']}/{scout_case['display_name']}",
                hpo_term=archive_term["phenotype_id"],
                is_group=key == "phenotype_groups",
            )


@click.command()
@click.option("--uri", required=True)
@click.option("--archive-uri", required=True)
@click.option("--dry", is_flag=True)
@click.option("--force", is_flag=True)
@click.argument("case_id")
def migrate(uri: str, archive_uri: str, case_id: str, dry: bool, force: bool):
    """Update all information that was manually annotated from a old instance."""
    scout_client = MongoClient(uri)
    scout_database = scout_client[uri.rsplit("/", 1)[-1]]
    scout_adapter = MongoAdapter(database=scout_database)
    scout_case = scout_adapter.case(case_id)
    if not force and scout_case.get("is_migrated"):
        print("case already migrated")
        return

    archive_client = MongoClient(archive_uri)
    archive_database = archive_client[archive_uri.rsplit("/", 1)[-1]]
    archive_case = archive_database.case.find_one(
        {"owner": scout_case["owner"], "display_name": scout_case["display_name"]}
    )

    archive_data = archive_info(archive_database, archive_case)

    if dry:
        print(ruamel.yaml.safe_dump(archive_data))
    else:
        # migrate_case(scout_adapter, scout_case, archive_data)
        pass


if __name__ == "__main__":
    migrate()
