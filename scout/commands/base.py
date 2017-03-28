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
from scout.commands.transfer import transfer
from scout.commands.setup import setup as setup_command
from scout.commands.convert import convert
from scout.commands.query import query as query_command
from scout.commands.view import view as view_command
from scout.commands.delete import delete

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
@click.option('-db', '--mongodb',
    default='scout',
    show_default=True,
    help='Name of mongo database',
)
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-port', '--port',
    default=27017,
    show_default=True,
    help="Specify on what port to listen for the mongod",
)
@click.option('-h', '--host',
    default='localhost',
    show_default=True,
    help="Specify the host for the mongo database.",
)
@click.option('-c', '--config',
    type=click.Path(exists=True),
    help="Specify the path to a config file with database info.",
)
@click.version_option(__version__)
@click.pass_context
def cli(context, mongodb, username, password, host, port, logfile, loglevel,
        config):
    """scout: manage interactions with a scout instance."""
    coloredlogs.install(log_level=loglevel)
    log.info("Running scout version %s", __version__)

    mongo_configs = {}
    configs = {}
    if config:
        log.debug("Use config file {0}".format(config))
        with open(config, 'r') as in_handle:
            configs = yaml.load(in_handle)

    mongo_configs['mongodb'] = (mongodb or configs.get('mongodb'))
    log.debug("Setting database name to %s", mongo_configs['mongodb'])

    mongo_configs['host'] = (host or configs.get('host'))
    log.debug("Setting host to {0}".format(mongo_configs['host']))

    mongo_configs['port'] = (port or configs.get('port'))
    log.debug("Setting port to {0}".format(mongo_configs['port']))

    mongo_configs['username'] = username or configs.get('username')
    mongo_configs['password'] = password or configs.get('password')
    mongo_configs['adapter'] = None
    # mongo uri looks like:
    # mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    if not context.invoked_subcommand == 'setup':
        try:
            client = get_connection(
                        host=mongo_configs['host'],
                        port=mongo_configs['port'],
                        username=mongo_configs['username'],
                        password=mongo_configs['password'],
                    )
        except ConnectionFailure:
            context.abort()
        
        database = client[mongo_configs['mongodb']]
        log.info("Test if mongod is running")
        try:
            database.test.find_one()
        except ServerSelectionTimeoutError as err:
            log.warning("Connection could not be established")
            context.abort()

        log.info("Setting up a mongo adapter")
        mongo_adapter = MongoAdapter(database)
        mongo_configs['adapter'] = mongo_adapter
    
    context.obj = mongo_configs


cli.add_command(load_command)
cli.add_command(transfer)
cli.add_command(wipe)
cli.add_command(setup_command)
cli.add_command(export)
cli.add_command(convert)
cli.add_command(query_command)
cli.add_command(view_command)
cli.add_command(delete)
