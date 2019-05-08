# -*- coding: utf-8 -*-
import sys
import logging

import click
import coloredlogs
import yaml

from flask.cli import FlaskGroup, current_app, with_appcontext
from scout.server.app import create_app

# General, logging
from scout import __version__

# Commands
from scout.commands.load import load as load_command
from scout.commands.export import export
from scout.commands.wipe_database import wipe
from scout.commands.setup import setup as setup_command
from scout.commands.convert import convert
from scout.commands.view import view as view_command
from scout.commands.delete import delete
from scout.commands.serve import serve
from scout.commands.update import update as update_command
from scout.commands.index_command import index as index_command
from scout.server import extensions

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.group(cls=FlaskGroup, create_app=create_app)
@click.option('--loglevel', default='INFO', type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.", show_default=True)
@click.option('--demo', is_flag=True, help="If the demo database should be used")
@click.option('-c', '--config', type=click.Path(exists=True))
@with_appcontext
def app_cli(loglevel, demo, config):
    """Entry point of Scout CLI"""
    log_format = None
    coloredlogs.install(level=loglevel, fmt=log_format)
    LOG.info("Running scout version %s", __version__)
    LOG.debug("Debug logging enabled.")
    # the only parameter used in config file will be omim_api_key
    # the other parameters will be taken from the current_app object
    if config:
        LOG.debug("Use config file %s", config)
        with open(config, 'r') as in_handle:
            cli_config = yaml.load(in_handle)
        current_app.config["OMIM_API_KEY"] = cli_config.get('omim_api_key')
    if demo:
        LOG.info('setting up connection to use database:"scout-demo"')
        client = current_app.config['MONGO_CLIENT']
        current_app.config["MONGO_DATABASE"] = client['scout-demo']
        extensions.store.init_app(current_app)


app_cli.add_command(query_command)
app_cli.add_command(load_command)
app_cli.add_command(wipe)
app_cli.add_command(setup_command)
app_cli.add_command(delete)
app_cli.add_command(export)
app_cli.add_command(convert)
app_cli.add_command(index_command)
app_cli.add_command(view_command)
app_cli.add_command(update_command)
app_cli.add_command(serve)
