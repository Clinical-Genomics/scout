"""
Cli functions to setup scout
"""

import logging

from pprint import pprint as pp


import pymongo
import click

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

# Import the resources to setup scout
from scout.resources import (hgnc_path, exac_path, mim2gene_path,
                             genemap2_path, hpogenes_path, hpoterms_path,
                             hpodisease_path)
from scout.resources import transcripts37_path as transcripts_path

# Import the functions to setup scout
from scout.build import build_institute

from scout.load import (load_hgnc_genes, load_hpo)

from scout.utils.handle import get_file_handle
from scout.utils.link import link_genes

log = logging.getLogger(__name__)

@click.command('database', short_help='Setup a basic scout instance')
@click.pass_context
def database(context):
    """Setup a scout database"""
    log.info("Running scout setup database")
    pp(context.__dict__)
    
    adapter = context.obj['adapter']

    log.info("Setting up database %s", context.obj['mongodb'])
    context.abort()
    log.info("Deleting previous database")
    for collection_name in adapter.db.collection_names():
        log.info("Deleting collection %s", collection_name)
        adapter.db.drop_collection(collection_name)
    log.info("Database deleted")

    institute_obj = build_institute(
        internal_id=institute_name,
        display_name=institute_name,
        sanger_recipients=[user_mail]
    )

    adapter.add_institute(institute_obj)

    user_obj = dict(
                _id=user_mail,
                email=user_mail,
                name=user_name,
                roles=['admin'],
                institutes=[institute_name])
    adapter.add_user(user_obj)

    # Load the genes and transcripts
    log.info("Loading hgnc file from {0}".format(hgnc_path))
    hgnc_handle = get_file_handle(hgnc_path)

    log.info("Loading ensembl transcript file from {0}".format(
                transcripts_path))
    transcripts_handle = get_file_handle(transcripts_path)

    log.info("Loading exac gene file from {0}".format(
                exac_path))
    exac_handle = get_file_handle(exac_path)

    log.info("Loading HPO gene file from {0}".format(
                hpogenes_path))
    hpo_genes_handle = get_file_handle(hpogenes_path)

    log.info("Loading mim2gene file from {0}".format(
                hpogenes_path))
    mim2gene_handle = get_file_handle(mim2gene_path)

    log.info("Loading genemap file from {0}".format(
                genemap2_path))
    genemap_handle = get_file_handle(genemap2_path)

    genes = link_genes(
        ensembl_lines=transcripts_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
    )
    load_hgnc_genes(adapter, genes)

    log.info("Loading hpo terms from file {0}".format(hpoterms_path))
    log.info("Loading hpo disease terms from file {0}".format(hpodisease_path))

    hpo_terms_handle = get_file_handle(hpoterms_path)
    disease_handle = get_file_handle(genemap2_path)

    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        disease_lines=disease_handle
    )
    
    log.info("Creating indexes")
    
    adapter.hgnc_collection.create_index([('build', pymongo.ASCENDING),
                                          ('chromosome', pymongo.ASCENDING)])

    log.info("Scout instance setup successful")

@click.command('demo', short_help='Setup a scout demo instance')
@click.pass_context
def demo(context):
    """Setup a scout demo instance. This instance will be populated with a 
       case a gene panel and some variants.
    """
    log.info("Running scout setup demo")
    pp(context.__dict__)
    


@click.group()
@click.pass_context
def setup(context):
    """
    Setup scout instances.
    """
    
    if context.invoked_subcommand == 'demo':
        # Update context.obj settings here
        log.info("Change database name to scout-demo")
        context.obj['mongodb'] = 'scout-demo'
    
    try:
        client = get_connection(
                    host=context.obj['host'],
                    port=context.obj['port'],
                    username=context.obj['username'],
                    password=context.obj['password'],
                )
    except ConnectionFailure:
        context.abort()
    
    database = client[context.obj['mongodb']]
    log.info("Test if mongod is running")
    try:
        database.test.find_one()
    except ServerSelectionTimeoutError as err:
        log.warning("Connection could not be established")
        log.warning("Please check if mongod is running")
        context.abort()

    log.info("Setting up a mongo adapter")
    mongo_adapter = MongoAdapter(database)
    context.obj['adapter'] = mongo_adapter
    

setup.add_command(database)
setup.add_command(demo)

