# -*- coding: utf-8 -*-
import click
import yaml

from scout import __version__, logger
from scout.log import init_log
from scout.adapter import MongoAdapter
from . import (load, transfer, wipe, genes, export, institute, hpo, panel,
               init_command, hgnc_query, convert)
from .cases import cases

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


@click.group()
@click.option('-l', '--logfile',
              type=click.Path(exists=False),
              help="Path to log file. If none logging is printed to stderr."
)
@click.option('--loglevel',
              default='INFO',
              type=click.Choice(LOG_LEVELS),
              help="Set the level of log output.",
              show_default=True,
)
@click.option('-db', '--mongodb')
@click.option('-u', '--username')
@click.option('-p', '--password')
@click.option('-port', '--port',
              help="Specify port to look for the mongo database")
@click.option('-h', '--host',
              help="Specify the host where to look for the mongo database.")
@click.option('-c', '--config',
              type=click.Path(exists=True),
              help="Specify the path to a config file with database info."
)
@click.version_option(__version__)
@click.pass_context
def cli(ctx, mongodb, username, password, host, port, logfile, loglevel,
        config):
    """Manage Scout interactions."""
    init_log(logger, logfile, loglevel)
    mongo_configs = {}
    configs = {}
    if config:
        logger.debug("Use config file {0}".format(config))
        with open(config, 'r') as in_handle:
            configs = yaml.load(in_handle)

    mongo_configs['mongodb'] = (mongodb or configs.get('mongodb') or
                                'variantDatabase')
    logger.debug("Setting mongodb to {0}".format(mongo_configs['mongodb']))

    mongo_configs['host'] = (host or configs.get('host') or 'localhost')
    logger.debug("Setting host to {0}".format(mongo_configs['host']))

    mongo_configs['port'] = (port or configs.get('port') or 27017)
    logger.debug("Setting port to {0}".format(mongo_configs['port']))

    mongo_configs['username'] = username or configs.get('username')
    mongo_configs['password'] = password or configs.get('password')

    logger.debug("Setting up a mongo adapter")
    mongo_adapter = MongoAdapter()
    logger.debug("Connecting to database")
    mongo_adapter.connect_to_database(
        database=mongo_configs['mongodb'],
        host=mongo_configs['host'],
        port=mongo_configs['port'],
        username=mongo_configs['username'],
        password=mongo_configs['password']
    )
    mongo_configs['adapter'] = mongo_adapter
    ctx.obj = mongo_configs


cli.add_command(load)
cli.add_command(transfer)
cli.add_command(wipe)
cli.add_command(genes)
cli.add_command(init_command)
cli.add_command(hpo)
cli.add_command(export)
cli.add_command(institute)
cli.add_command(panel)
cli.add_command(cases)
cli.add_command(convert)
cli.add_command(hgnc_query)
