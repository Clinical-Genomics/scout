# -*- coding: utf-8 -*-
import datetime
import logging
from pprint import pprint as pp

import click
import coloredlogs
import pymongo
import yaml

# General, logging
from scout import __version__
from scout.adapter.client import get_connection

# Adapter stuff
from scout.adapter.mongo import MongoAdapter

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
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Specify the path to a config file with database info.",
)
@click.version_option(__version__)
@click.pass_context
def check_panels(context, mongodb, username, password, authdb, host, port, loglevel, config):
    """scout: manage interactions with a scout instance."""
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

    LOG.info("Setting database name to %s", mongo_config["mongodb"])
    LOG.debug("Setting host to %s", mongo_config["host"])
    LOG.debug("Setting port to %s", mongo_config["port"])

    # Connection validity will be checked in adapter.client
    client = get_connection(**mongo_config)

    database = client[mongo_config["mongodb"]]

    LOG.info("Setting up a mongo adapter")
    mongo_config["client"] = client
    adapter = MongoAdapter(database)

    cases_compromised = 0
    compromised_cases = []
    cases = 0
    panel_genes_incorrect = {}
    variants_found = ""
    panel_issue_found = ""
    for case_obj in adapter.case_collection.find(no_cursor_timeout=True).sort("updated_at", -1):
        if case_obj.get("updated_at") < datetime.datetime(2020, 9, 8):
            break
        #        if cases_compromised >= 20:
        #            break
        case_compromised = False
        for panel_info in case_obj.get("panels", []):
            panel_name = panel_info["panel_name"]
            if not panel_info.get("is_default", False):
                continue

            if panel_genes_incorrect.get(panel_name, None) is not None:
                if len(panel_genes_incorrect[panel_name]) > 0:
                    case_compromised = True
            else:
                panel_obj = adapter.gene_panel(panel_name)
                if not panel_obj:
                    LOG.warning("Panel: {0} does not exist in database".format(panel_name))
                    continue

                symbols_compromised = []
                for panel_gene in panel_obj["genes"]:
                    gene_hgnc_id = panel_gene["hgnc_id"]
                    hgnc_symbol_panel = panel_gene["symbol"]
                    hgnc_gene_from_id = adapter.hgnc_gene(gene_hgnc_id)
                    hgnc_symbol_hgnc = hgnc_gene_from_id.get("hgnc_symbol")

                    if hgnc_symbol_panel != hgnc_symbol_hgnc:
                        case_compromised = True
                        symbols_compromised.append(hgnc_symbol_hgnc)
                        panel_issue_found += "Case {} panel {} gene symbol {} differes from current hgnc symbol {}\n".format(
                            case_obj["display_name"],
                            panel_name,
                            hgnc_symbol_panel,
                            hgnc_symbol_hgnc,
                        )

                panel_genes_incorrect[panel_name] = symbols_compromised

            if panel_genes_incorrect.get(panel_name, None):
                for variant in adapter.variants(
                    case_obj["_id"],
                    query={
                        "hgnc_symbols": panel_genes_incorrect[panel_name],
                    },
                    nr_of_variants=-1,
                    sort_key="rank_score",
                ):
                    if variant.get("rank_score") > 15:
                        variants_found += "{} case {} {} variant {} {} {}.\n".format(
                            variant["institute"],
                            case_obj["_id"],
                            case_obj["display_name"],
                            variant["display_name"],
                            variant["rank_score"],
                            variant["hgnc_symbols"],
                        )

        cases += 1
        if case_compromised:
            cases_compromised += 1
            compromised_cases.append(case_obj["_id"])
            LOG.debug(
                "Case {} compromised.".format(
                    case_obj["display_name"],
                )
            )
        else:
            LOG.debug(
                "Case {} ok.".format(
                    case_obj["display_name"],
                )
            )

    LOG.warning("{} cases out of {} were compromised.".format(cases_compromised, cases))

    for panel, symbols in panel_genes_incorrect.items():
        LOG.warning("Panel {} had {} symbols compromised".format(panel, len(symbols)))

    LOG.warning("Panel issues:\n{}".format(panel_issue_found))

    LOG.warning("Variants of interest: {} ".format(variants_found))


if __name__ == "__main__":
    check_panels()
