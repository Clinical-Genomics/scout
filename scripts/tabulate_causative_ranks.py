# -*- coding: utf-8 -*-
import datetime
import logging

import click
import coloredlogs
import yaml

# General, logging
from scout import __version__
from scout.adapter.client import get_connection

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.constants import CLINICAL_FILTER_BASE, CLINICAL_FILTER_BASE_SV

try:
    from scoutconfig import *
except ImportError:
    pass

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.command()
@click.option(
    "--loglevel",
    default="INFO",
    type=click.Choice(LOG_LEVELS),
    help="Set the level of log output.",
    show_default=True,
)
@click.option("-db", "--mongodb", help="Name of mongo database [scout]")
@click.option("-u", "--username")
@click.option("-p", "--password")
@click.option("-a", "--authdb", help="database to use for authentication")
@click.option("-port", "--port", help="Specify on what port to listen for the mongod")
@click.option("-h", "--host", help="Specify the host for the mongo database.")
@click.option("--uri")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Specify the path to a config file with database info.",
)
@click.version_option(__version__)
@click.pass_context
def tabulate_causative_panel_rank(
    context, mongodb, username, password, authdb, host, port, loglevel, config, uri
):
    """Establish interaction with a scout instance to tabulate the
    rank score, rank and clinical filter within panel rank for all variants marked causative.
    Write these to stdout via Click.
    """
    coloredlogs.install(level=loglevel)

    LOG.info("Running scout version %s", __version__)
    LOG.debug("Debug logging enabled.")

    mongo_config = {}
    cli_config = {}
    if config:
        LOG.debug("Use config file %s", config)
        with open(config, "r") as in_handle:
            cli_config = yaml.load(in_handle, Loader=yaml.SafeLoader)

    mongo_config["mongodb"] = mongodb or cli_config.get("mongodb") or "scout"

    mongo_config["host"] = host or cli_config.get("host") or "localhost"
    mongo_config["port"] = port or cli_config.get("port") or 27017
    mongo_config["username"] = username or cli_config.get("username")
    mongo_config["password"] = password or cli_config.get("password")
    mongo_config["authdb"] = authdb or cli_config.get("authdb") or mongo_config["mongodb"]
    mongo_config["omim_api_key"] = cli_config.get("omim_api_key")
    mongo_config["uri"] = uri or cli_config.get("mongo_uri")

    LOG.info("Setting database name to %s", mongo_config["mongodb"])
    LOG.debug("Setting host to %s", mongo_config["host"])
    LOG.debug("Setting port to %s", mongo_config["port"])
    LOG.debug("Setting uri to %s", mongo_config["uri"])

    # Connection validity will be checked in adapter.client
    client = get_connection(**mongo_config)

    database = client[mongo_config["mongodb"]]

    LOG.info("Setting up a mongo adapter")
    mongo_config["client"] = client
    adapter = MongoAdapter(database)

    # causative, rank, RANK IN DEFAULT PANEL, rankscore, model version, date, inheritance models, ACMG

    click.echo(f"Case\tOwner\tDate\tPanels\tCategory\tVer\tRank score\tRank\tClin rank\tBest rank")

    causatives = []

    institutes = list(adapter.institutes())

    for institute_obj in institutes:
        inst_causatives = list(adapter.institute_causatives(institute_obj=institute_obj))
        for variant_obj in inst_causatives:

            if variant_obj["category"] not in ["sv", "snv"]:
                continue

            case_obj = adapter.case(variant_obj["case_id"])
            if not case_obj:
                continue

            # fill in query with default panels
            default_panels = []
            for panel in case_obj.get("panels", []):
                if panel.get("is_default"):
                    default_panels.append(panel["panel_name"])

            if case_obj.get("hpo_clinical_filter"):
                clinical_filter_panels = ["hpo"]
            else:
                clinical_filter_panels = default_panels

            if variant_obj["category"] == "snv":
                clinical_filter_dict = CLINICAL_FILTER_BASE
                clinical_filter_dict.update(
                    {
                        "gnomad_frequency": str(institute_obj["frequency_cutoff"]),
                        "gene_panels": clinical_filter_panels,
                    }
                )
            elif variant_obj["category"] == "sv":
                clinical_filter_dict = CLINICAL_FILTER_BASE_SV
                clinical_filter_dict.update(
                    {
                        "gene_panels": clinical_filter_panels,
                    }
                )

            query = clinical_filter_dict
            query["rank_score"] = variant_obj["rank_score"]
            count_higher_gte_rank_score_with_clinical_filter = adapter.count_variants(
                variant_obj["case_id"],
                query,
                None,
                category=variant_obj["category"],
                build="37",
            )
            best_rank = variant_obj["variant_rank"]
            if count_higher_gte_rank_score_with_clinical_filter == 0:
                count_higher_gte_rank_score_with_clinical_filter = "NA"
            else:
                best_rank = min(best_rank, count_higher_gte_rank_score_with_clinical_filter)

            # decorate variant
            variant_genes = variant_obj.get("genes", [])
            #            variant_obj.update(predictions(variant_genes))
            variant_obj["case_obj"] = {
                "display_name": case_obj["display_name"],
                "individuals": case_obj["individuals"],
                "status": case_obj.get("status"),
                "partial_causatives": case_obj.get("partial_causatives", []),
                "rank_model_version": case_obj.get("rank_model_version"),
                "sv_rank_model_version": case_obj.get("sv_rank_model_version"),
            }

            causatives.append(variant_obj)
            rank_model_version = case_obj.get("rank_model_version")
            if variant_obj["category"] == "sv":
                rank_model_version = f"{case_obj.get('sv_rank_model_version')}"

            analysis_date = case_obj.get("analysis_date")
            owner = case_obj.get("owner")

            click.echo(
                f"{variant_obj['case_obj']['display_name']}\t{owner}\t{analysis_date}\t{clinical_filter_panels}\t{variant_obj['category']}\t{rank_model_version}\t{variant_obj['rank_score']}\t{variant_obj['variant_rank']}\t{count_higher_gte_rank_score_with_clinical_filter}\t{best_rank}"
            )


if __name__ == "__main__":
    tabulate_causative_panel_rank()
