# -*- coding: utf-8 -*-
import sys
import logging

from pprint import pprint as pp

import click
import coloredlogs
import yaml

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import (ConnectionFailure, OperationFailure)

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

try:
    from scoutconfig import *
except ImportError:
    pass

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


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
    # log_format = "%(message)s" if sys.stdout.isatty() else None
    log_format = None
    coloredlogs.install(level=loglevel, fmt=log_format)
    LOG.info("Running scout version %s", __version__)
    LOG.debug("Debug logging enabled.")

    mongo_config = {}
    cli_config = {}
    if config:
        LOG.debug("Use config file %s", config)
        with open(config, 'r') as in_handle:
            cli_config = yaml.load(in_handle)

    mongo_config['mongodb'] = (mongodb or cli_config.get('mongodb') or 'scout')
    if demo:
        mongo_config['mongodb'] = 'scout-demo'

    mongo_config['host'] = (host or cli_config.get('host') or 'localhost')
    mongo_config['port'] = (port or cli_config.get('port') or 27017)
    mongo_config['username'] = username or cli_config.get('username')
    mongo_config['password'] = password or cli_config.get('password')
    mongo_config['authdb'] = authdb or cli_config.get('authdb') or mongo_config['mongodb']
    mongo_config['omim_api_key'] = cli_config.get('omim_api_key')

    if context.invoked_subcommand in ('setup', 'serve'):
        mongo_config['adapter'] = None
    else:
        LOG.info("Setting database name to %s", mongo_config['mongodb'])
        LOG.debug("Setting host to %s", mongo_config['host'])
        LOG.debug("Setting port to %s", mongo_config['port'])

        try:
            client = get_connection(**mongo_config)
        except ConnectionFailure:
            context.abort()

        database = client[mongo_config['mongodb']]

        LOG.info("Setting up a mongo adapter")
        mongo_config['client'] = client
        adapter = MongoAdapter(database)
        mongo_config['adapter'] = adapter
        
        LOG.info("Check if authenticated...")
        try:
            for ins_obj in adapter.institutes():
                pass
        except OperationFailure as err:
            LOG.info("User not authenticated")
            context.abort()
        

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
