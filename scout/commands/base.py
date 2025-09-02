import logging

import click
import coloredlogs
import yaml
from flask.cli import FlaskGroup, with_appcontext

# General, logging
from scout import __version__
from scout.commands.convert import convert
from scout.commands.delete import delete
from scout.commands.download import download as download_command
from scout.commands.export import export
from scout.commands.index_command import index as index_command
from scout.commands.load import load as load_command
from scout.commands.serve import serve
from scout.commands.setup import setup as setup_command
from scout.commands.update import update as update_command
from scout.commands.view import view as view_command
from scout.commands.wipe_database import wipe
from scout.server.app import create_app
from scout.utils.config import load_config

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG = logging.getLogger(__name__)


@click.pass_context
def loglevel(ctx):
    """Set app cli log level"""
    log_level = ctx.find_root().params.get("loglevel")
    log_format = None
    coloredlogs.install(level=log_level, fmt=log_format)
    LOG.info("Running scout version %s", __version__)
    LOG.debug("Debug logging enabled.")


@click.pass_context
def get_app(ctx=None):
    """Create an app with the correct config or with default app params"""

    loglevel()  # Set up log level even before creating the app object
    options = ctx.find_root()

    # YAML config (deprecated)
    cli_config = {}
    if options.params.get("config"):
        LOG.warning(
            "Support for launching Scout using a .yaml config file is deprecated "
            "and will be removed in the next major release (5.0). "
            "Use a PYTHON (.py) config file instead.",
        )
        with open(options.params["config"], "r") as in_handle:
            cli_config = yaml.load(in_handle, Loader=yaml.SafeLoader)
            if cli_config.get("mongodb"):
                cli_config["mongo_dbname"] = cli_config.pop("mongodb")

    if options.params.get("demo"):
        cli_config["demo"] = "scout-demo"

    # python config file
    flask_conf = options.params.get("flask_config")

    # collect CLI options into a dict
    cli_options = {
        "MONGO_DBNAME": (
            "scout-demo" if options.params.get("demo") else options.params.get("mongodb")
        ),
        "MONGO_HOST": options.params.get("host"),
        "MONGO_PORT": options.params.get("port"),
        "MONGO_USERNAME": options.params.get("username"),
        "MONGO_PASSWORD": options.params.get("password"),
        "MONGO_URI": options.params.get("mongo_uri"),
        "OMIM_API_KEY": cli_config.get("omim_api_key"),
    }

    # Echo the database name if demo mode is used
    if options.params.get("demo"):
        click.echo(f"Demo mode - database name is: {cli_options['MONGO_DBNAME']}")

    try:
        config = load_config(cli_options=cli_options, cli_config=cli_config, flask_conf=flask_conf)
        app = create_app(config=config)
    except SyntaxError as err:
        LOG.error(err)
        raise click.Abort

    return app


@click.version_option(__version__)
@click.group(
    cls=FlaskGroup,
    create_app=get_app,
    invoke_without_command=True,
    add_default_commands=False,
    add_version_option=False,
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Path to a YAML config file with database info.",
)
@click.option(
    "--loglevel",
    default="INFO",
    type=click.Choice(LOG_LEVELS),
    help="Set the level of log output.",
    show_default=True,
)
@click.option("--demo", is_flag=True, help="If the demo database should be used")
@click.option("-db", "--mongodb", help="Name of mongo database [scout]")
@click.option("-uri", "--mongo-uri", help="MongoDB connection string")
@click.option("-u", "--username")
@click.option("-p", "--password")
@click.option("-a", "--authdb", help="database to use for authentication")
@click.option("-port", "--port", help="Specify on what port to listen for the mongod")
@click.option("-h", "--host", help="Specify the host for the mongo database.")
@click.option(
    "-f",
    "--flask-config",
    type=click.Path(exists=True),
    help="Path to a PYTHON config file",
)
@with_appcontext
def cli(**_):
    """scout: manage interactions with a scout instance."""


# Register all commands
cli.add_command(load_command)
cli.add_command(wipe)
cli.add_command(setup_command)
cli.add_command(delete)
cli.add_command(export)
cli.add_command(convert)
cli.add_command(index_command)
cli.add_command(view_command)
cli.add_command(update_command)
cli.add_command(download_command)
cli.add_command(serve)
