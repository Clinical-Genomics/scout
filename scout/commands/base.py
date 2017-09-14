# -*- coding: utf-8 -*-
import logging

import click
import coloredlogs
import yaml

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

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

from scout.adapter.utils import check_connection

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
log = logging.getLogger(__name__)


@click.group()
@click.option('-l', '--logfile',
    type=click.Path(exists=False),
    help="Path to log file. If none logging is printed to stderr.",
)
@click.option('--loglevel',
    default='INFO',
    type=click.Choice(LOG_LEVELS),
    help="Set the level of log output.",
    show_default=True,
)
@click.option('-db', '--mongodb', help='Name of mongo database')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-port', '--port', help="Specify on what port to listen for the mongod")
@click.option('-h', '--host', help="Specify the host for the mongo database.")
@click.option('-c', '--config',
    type=click.Path(exists=True),
    help="Specify the path to a config file with database info.",
)
@click.option('--demo', is_flag=True, help="If the demo database should be used")
@click.version_option(__version__)
@click.pass_context
def cli(context, mongodb, username, password, host, port, logfile, loglevel,
        config, demo):
    """scout: manage interactions with a scout instance."""
    coloredlogs.install(level=loglevel)
    log.info("Running scout version %s", __version__)
    log.debug("Debug logging enabled.")

    mongo_configs = {}
    configs = {}
    if config:
        log.debug("Use config file {0}".format(config))
        with open(config, 'r') as in_handle:
            configs = yaml.load(in_handle)

    mongo_configs['mongodb'] = (mongodb or configs.get('mongodb') or 'scout')
    if demo:
        mongo_configs['mongodb'] = 'scout-demo'

    mongo_configs['host'] = (host or configs.get('host') or 'localhost')
    mongo_configs['port'] = (port or configs.get('port') or 27017)
    mongo_configs['username'] = username or configs.get('username')
    mongo_configs['password'] = password or configs.get('password')
    # mongo uri looks like:
    # mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
        
        
    
    if context.invoked_subcommand not in ('setup', 'serve'):
        log.info("Setting database name to %s", mongo_configs['mongodb'])
        log.debug("Setting host to {0}".format(mongo_configs['host']))
        log.debug("Setting port to {0}".format(mongo_configs['port']))
        
        valid_connection = check_connection(
            host=mongo_configs['host'], 
            port=mongo_configs['port'], 
            username=mongo_configs['username'], 
            password=mongo_configs['password'], )
    
        log.info("Test if mongod is running")
        if not valid_connection:
            log.warning("Connection could not be established")
            context.abort()
        
        try:
            client = get_connection(**mongo_configs)
        except ConnectionFailure:
            context.abort()

        database = client[mongo_configs['mongodb']]
        # try:
        #     database.test.find_one()
        # except ServerSelectionTimeoutError as err:
        #     log.warning("Connection could not be established")
        #     context.abort()

        log.info("Setting up a mongo adapter")
        mongo_adapter = MongoAdapter(database)
        mongo_configs['adapter'] = mongo_adapter
    else:
        mongo_configs['adapter'] = None

    context.obj = mongo_configs


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
