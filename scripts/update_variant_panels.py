# -*- coding: utf-8 -*-
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
def update_panels(context, mongodb, username, password, authdb, host, port, loglevel, config):
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

    requests = []

    for case_obj in adapter.case_collection.find():
        # pp(case_obj)

        gene_to_panels = adapter.gene_to_panels(case_obj)

        variants = adapter.variant_collection.find(
            {"case_id": case_obj["_id"], "category": "snv", "variant_type": "clinical"}
        )

        for variant_obj in variants:
            panel_names = set()
            for hgnc_id in variant_obj["hgnc_ids"]:
                gene_panels = gene_to_panels.get(hgnc_id, set())
                panel_names = panel_names.union(gene_panels)

            if panel_names:
                operation = pymongo.UpdateOne(
                    {"_id": variant_obj["_id"]}, {"$set": {"panels": list(panel_names)}}
                )
                requests.append(operation)

            if len(requests) > 5000:
                adapter.variant_collection.bulk_write(requests, ordered=False)
                requests = []

        if requests:
            adapter.variant_collection.bulk_write(requests, ordered=False)
            requests = []


if __name__ == "__main__":
    update_panels()
