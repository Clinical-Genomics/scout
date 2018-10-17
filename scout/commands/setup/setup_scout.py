"""
Cli functions to setup scout

There are two options. 
`scout setup demo` will setup a database that are loaded with more example 
data but the gene definitions etc are reduced.

`scout setup database` will create a full scale instance of scout. There will not be any cases 
and one admin user is added.



"""
import logging
import datetime

import pymongo
import click

from pprint import pprint as pp

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

from scout.load.setup import setup_scout

LOG = logging.getLogger(__name__)

def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()

@click.command('database', short_help='Setup a basic scout instance')
@click.option('-i', '--institute-name', type=str)
@click.option('-u', '--user-name', type=str)
@click.option('-m', '--user-mail', type=str)
@click.option('--api-key', help='Specify the api key')
@click.option('--yes', 
    is_flag=True, 
    callback=abort_if_false,
    expose_value=False,
    prompt='This will delete existing database, do you wish to continue?')
@click.pass_context
def database(context, institute_name, user_name, user_mail, api_key):
    """Setup a scout database."""
    LOG.info("Running scout setup database")

    # Fetch the omim information
    api_key = api_key or context.obj.get('omim_api_key')
    if not api_key:
        LOG.warning("Please provide a omim api key with --api-key")
        context.abort()

    institute_name = institute_name or context.obj['institute_name']
    user_name = user_name or context.obj['user_name']
    user_mail = user_mail or context.obj['user_mail']

    adapter = context.obj['adapter']

    LOG.info("Setting up database %s", context.obj['mongodb'])
    
    setup_scout(
        adapter=adapter,
        institute_id=institute_name, 
        user_name=user_name, 
        user_mail = user_mail, 
        api_key=api_key
    )

@click.command('demo', short_help='Setup a scout demo instance')
@click.pass_context
def demo(context):
    """Setup a scout demo instance. This instance will be populated with a
       case, a gene panel and some variants.
    """
    LOG.info("Running scout setup demo")
    institute_name = context.obj['institute_name']
    user_name = context.obj['user_name']
    user_mail = context.obj['user_mail']

    adapter = context.obj['adapter']

    LOG.info("Setting up database %s", context.obj['mongodb'])
    
    setup_scout(
        adapter=adapter,
        institute_id=institute_name, 
        user_name=user_name, 
        user_mail = user_mail, 
        demo=True
    )

from scout.demo.resources.generate_test_data import (generate_hgnc, generate_genemap2, generate_mim2genes, 
generate_exac_genes, generate_ensembl_genes, generate_ensembl_transcripts, generate_hpo_files)
from scout.demo import panel_path

from scout.parse.panel import parse_gene_panel

@click.group()
@click.option('-i', '--institute',
    default='cust000',
    show_default=True,
    help='Name of initial institute',
)
@click.option('-e', '--user-mail',
    default='clark.kent@mail.com',
    show_default=True,
    help='Mail of initial user',
)
@click.option('-n', '--user-name',
    default='Clark Kent',
    show_default=True,
    help='Name of initial user',
)
@click.pass_context
def setup(context, institute, user_mail, user_name):
    """
    Setup scout instances.
    """

    context.obj['institute_name'] = institute
    context.obj['user_name'] = user_name
    context.obj['user_mail'] = user_mail

    if context.invoked_subcommand == 'demo':
        # Update context.obj settings here
        LOG.debug("Change database name to scout-demo")
        context.obj['mongodb'] = 'scout-demo'

    LOG.info("Setting database name to %s", context.obj['mongodb'])
    LOG.debug("Setting host to %s", context.obj['host'])
    LOG.debug("Setting port to %s", context.obj['port'])
    try:
        client = get_connection(
                    host=context.obj['host'],
                    port=context.obj['port'],
                    username=context.obj['username'],
                    password=context.obj['password'],
                    mongodb = context.obj['mongodb']
                )
    except ConnectionFailure:
        context.abort()

    LOG.info("connecting to database %s", context.obj['mongodb'])
    database = client[context.obj['mongodb']]
    LOG.info("Test if mongod is running")
    try:
        LOG.info("Test if mongod is running")
        database.test.find_one()
    except ServerSelectionTimeoutError as err:
        LOG.warning("Connection could not be established")
        LOG.warning("Please check if mongod is running")
        context.abort()

    LOG.info("Setting up a mongo adapter")
    mongo_adapter = MongoAdapter(database)
    context.obj['adapter'] = mongo_adapter


setup.add_command(database)
setup.add_command(demo)
