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

@click.pass_context
def loglevel(ctx):
    """Set app cli log level"""
    loglevel = ctx.find_root().params["loglevel"]
    log_format = None
    coloredlogs.install(level=loglevel, fmt=log_format)
    LOG.info("Running scout version %s", __version__)
    LOG.debug("Debug logging enabled.")


@click.pass_context
def get_app(ctx):
    """Create an app with the correct config or with default app params"""

    # store provided params into a options variable
    options = ctx.find_root()
    cli_config = {}
    # if a .yaml config file was provided use its params to intiate the app
    if options.params.get("config"):
        with open(options.params["config"], 'r') as in_handle:
            cli_config = yaml.load(in_handle, Loader=yaml.FullLoader)

    if options.params.get("demo"):
        cli_config['demo'] = 'scout-demo'

    app = create_app(config=dict(
        MONGO_DBNAME = cli_config.get('demo') or options.params.get("mongodb") or cli_config.get('mongodb') or 'scout',
        MONGO_HOST = options.params.get("host") or cli_config.get('host') or 'localhost',
        MONGO_PORT = options.params.get("port") or cli_config.get('port') or 27017,
        MONGO_USERNAME = options.params.get("username") or cli_config.get('username'),
        MONGO_PASSWORD = options.params.get("password") or cli_config.get('password'),
        OMIM_API_KEY = cli_config.get('omim_api_key'),
    ))
    return app


@click.version_option(__version__)
@click.group(cls=FlaskGroup, create_app=get_app, invoke_without_command=True, add_default_commands=False, add_version_option=False)
@click.option('-c', '--config', type=click.Path(exists=True),
              help="Specify the path to a config file with database info.")
@click.option('--loglevel', default='DEBUG', type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.", show_default=True)
@click.option('--demo', is_flag=True, help="If the demo database should be used")
@click.option('-db', '--mongodb', help='Name of mongo database [scout]')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-a', '--authdb', help='database to use for authentication')
@click.option('-port', '--port', help="Specify on what port to listen for the mongod")
@click.option('-h', '--host', help="Specify the host for the mongo database.")
@with_appcontext
def cli(**_):
    """scout: manage interactions with a scout instance."""
    loglevel()
    pass


cli.add_command(load_command)
cli.add_command(wipe)
cli.add_command(setup_command)
cli.add_command(delete)
cli.add_command(export)
cli.add_command(convert)
cli.add_command(index_command)
cli.add_command(view_command)
cli.add_command(update_command)
cli.add_command(serve)
