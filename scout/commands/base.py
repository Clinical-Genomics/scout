# -*- coding: utf-8 -*-
import logging

import click
import coloredlogs
import yaml

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import ConnectionFailure

# General, logging
from scout import __version__

# Commands
from scout.commands.load import load as load_command
from scout.commands.export import export
from scout.commands.wipe_database import wipe
from scout.commands.setup import setup as setup_command
from scout.commands.convert import convert
from scout.commands.query import query as query_command
from scout.commands.view import view as view_command
from scout.commands.delete import delete
from scout.commands.serve import serve
from scout.commands.update import update as update_command
from scout.commands.index_command import index as index_command

from scout.adapter.utils import check_connection

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
log = logging.getLogger(__name__)


@click.group()
@click.option('--loglevel', default='INFO', type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.", show_default=True)
@click.option('-db', '--mongodb', help='Name of mongo database [scout]')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-a', '--authdb', help='database to use for authentication')
@click.option('-port', '--port', help="Specify on what port to listen for the mongod")
@click.option('-h', '--host', help="Specify the host for the mongo database.")
@click.option('-c', '--config', type=click.Path(exists=True),
              help="Specify the path to a config file with database info.")
@click.option('--demo', is_flag=True, help="If the demo database should be used")
@click.version_option(__version__)
@click.pass_context
def cli(context, mongodb, username, password, authdb, host, port, loglevel, config, demo):
    """scout: manage interactions with a scout instance."""
    coloredlogs.install(level=loglevel)
    log.info("Running scout version %s", __version__)
    log.debug("Debug logging enabled.")

    mongo_config = {}
    if config:
        log.debug("Use config file %s", config)
        with open(config, 'r') as in_handle:
            cli_config = yaml.load(in_handle)
    else:
        cli_config = {}

    mongo_config['mongodb'] = (mongodb or cli_config.get('mongodb') or 'scout')
    if demo:
        mongo_config['mongodb'] = 'scout-demo'

    mongo_config['host'] = (host or cli_config.get('host') or 'localhost')
    mongo_config['port'] = (port or cli_config.get('port') or 27017)
    mongo_config['username'] = username or cli_config.get('username')
    mongo_config['password'] = password or cli_config.get('password')
    mongo_config['authdb'] = authdb or cli_config.get('authdb') or mongo_config['mongodb']
    # mongo uri looks like:
    # mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]

    if context.invoked_subcommand in ('setup', 'serve'):
        mongo_config['adapter'] = None
    else:
        log.info("Setting database name to %s", mongo_config['mongodb'])
        log.debug("Setting host to %s", mongo_config['host'])
        log.debug("Setting port to %s", mongo_config['port'])

        valid_connection = check_connection(
            host=mongo_config['host'],
            port=mongo_config['port'],
            username=mongo_config['username'],
            password=mongo_config['password'],
            authdb=mongo_config['authdb'],
        )

        log.info("Test if mongod is running")
        if not valid_connection:
            log.warning("Connection could not be established")
            context.abort()

        try:
            client = get_connection(**mongo_config)
        except ConnectionFailure:
            context.abort()

        database = client[mongo_config['mongodb']]

        log.info("Setting up a mongo adapter")
        mongo_config['adapter'] = MongoAdapter(database)

    context.obj = mongo_config


cli.add_command(load_command)
cli.add_command(wipe)
cli.add_command(setup_command)
cli.add_command(export)
cli.add_command(convert)
cli.add_command(query_command)
cli.add_command(view_command)
cli.add_command(delete)
cli.add_command(serve)
cli.add_command(update_command)
cli.add_command(index_command)
