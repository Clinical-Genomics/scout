"""Command to dump the scout database

Since the variants collection is very large this dump will be optional.

"""
import logging
import subprocess
from subprocess import CalledProcessError

import click

from flask import current_app
from flask.cli import with_appcontext

LOG = logging.getLogger(__name__)


@click.command("database", short_help="Export collections of scout")
@click.option(
    "--out",
    "-o",
    type=click.Path(exists=False),
    help="Directory to store the mongodump. Default: ./dump",
)
@click.option("--uri", help="mongodb uri")
@click.option("--all-collections", is_flag=True, help="Include variant collection")
@with_appcontext
def database(out, all_collections, uri):
    """Export collections of scout with mongodump. As a default only the most vital collections will be dumped.

    The database can be restored by running `mongorestore --gzip path/to/dump`
    """
    LOG.info("Running scout export database")
    dump_command = ["mongodump", "--gzip"]
    db_name = current_app.config.get("MONGO_DBNAME", "scout")
    if out:
        dump_command.extend(["--out", out])

    if not all_collections:
        LOG.info("Excluding variants collection")
        dump_command.extend(["--excludeCollection", "variant"])
        LOG.info("Excluding exons collection")
        dump_command.extend(["--excludeCollection", "exon"])
        LOG.info("Excluding transcripts collection")
        dump_command.extend(["--excludeCollection", "transcript"])
        LOG.info("Excluding hgnc_gene collection")
        dump_command.extend(["--excludeCollection", "hgnc_gene"])
        LOG.info("Excluding hpo_terms collection")
        dump_command.extend(["--excludeCollection", "hpo_term"])
        LOG.info("Excluding disease_terms collection")
        dump_command.extend(["--excludeCollection", "disease_term"])

    if uri:
        dump_command.extend(["--uri", uri])
    else:
        # Can not use both uri and login credentials
        dump_command.extend(["--db", db_name])
        host = current_app.config.get("MONGO_HOST", "localhost")
        dump_command.extend(["--host", host])
        port = str(current_app.config.get("MONGO_PORT", 27017))
        dump_command.extend(["--port", port])
        username = current_app.config.get("MONGO_USERNAME")
        if username:
            password = current_app.config.get("MONGO_PASSWORD")
            if password is None:
                LOG.warning("Please provide a password since username")
                return
            dump_command.extend(["--username", username])
            dump_command.extend(["--password", password])
    try:
        output = subprocess.run(dump_command, shell=False)
    except CalledProcessError as err:
        LOG.warning("Something went wrong when dumping database")
        raise err
    LOG.info("Scout was succesfully dumped")
