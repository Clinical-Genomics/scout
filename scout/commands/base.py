import click

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
@click.option('-db', '--mongodb', 
              default='variantDatabase',
              show_default=True,
)
@click.option('-u', '--username', 
              type=str
)
@click.option('-p', '--password',
              type=str
)
@click.option('-port', '--port', 
              default=27017,
              show_default=True,
              help="Specify port to look for the mongo database"
)
@click.option('-h', '--host', 
              default='localhost', 
              show_default=True,
              help="Specify the host where to look for the mongo database."
)
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
        configs = ConfigObj(config)

    if mongodb:
        mongo_configs['mongodb'] = mongodb
    else:
        mongo_configs['mongodb'] = configs.get('mongodb', 'variantDatabase')
    logger.debug("Setting mongodb to {0}".format(mongo_configs['mongodb']))

    if host:
        mongo_configs['host'] = host
    else:
        mongo_configs['host'] = configs.get('host', 'localhost')
    logger.debug("Setting host to {0}".format(mongo_configs['host']))

    if port:
        mongo_configs['port'] = port
    else:
        mongo_configs['port'] = int(configs.get('port', 27017))
    logger.debug("Setting port to {0}".format(mongo_configs['port']))

    if username:
        mongo_configs['username'] = username
    else:
        mongo_configs['username'] = configs.get('username')

    if password:
        mongo_configs['password'] = password
    else:
        mongo_configs['password'] = configs.get('password')

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
