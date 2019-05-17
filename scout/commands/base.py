# -*- coding: utf-8 -*-
import sys
import logging

import click
import coloredlogs
import yaml

from flask.cli import FlaskGroup, current_app, with_appcontext
from scout.server.app import create_app
from scout.server import extensions

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

    if ctx.find_root().params["scout_version"]:
        # display version and exit
        return

    LOG.debug("Debug logging enabled.")


@click.pass_context
@click.version_option(__version__)
def get_app(ctx):
    """Create an app with the correct config or with default app params"""
    # if a .yaml config file was provided use its params to intiate the app
    if ctx.find_root().params["config"]:
        cli_config = {}
        with open(ctx.find_root().params["config"], 'r') as in_handle:
            cli_config = yaml.load(in_handle, Loader=yaml.FullLoader)
            app = create_app(config=dict(
                DEBUG=True,
                MONGO_DBNAME = cli_config.get('mongodb'),
                MONGO_PORT = cli_config.get('port'),
                MONGO_USERNAME = cli_config.get('username'),
                MONGO_PASSWORD = cli_config.get('password'),
                ))
        return app

    # Otherwise intialize app using SCOUT_CONF envvar or default config file
    if ctx.find_root().params["demo"]:
        return create_app(config=dict(MONGO_DBNAME='scout-demo', DEBUG=True))
    return create_app()


@click.group(cls=FlaskGroup, create_app=get_app, invoke_without_command=True, add_default_commands=False)
@click.option('-c', '--config', type=click.Path(exists=True),
              help="Specify the path to a config file with database info.")
@click.option('--loglevel', default='DEBUG', type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.", show_default=True)
@click.option('--demo', is_flag=True, help="If the demo database should be used")
@click.option('-v', 'scout_version', is_flag=True, help="Display version of Scout")
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
