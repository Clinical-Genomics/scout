"""
Cli functions to setup scout
"""
import logging
import datetime
import yaml

import pymongo
import click

from pprint import pprint as pp

# Adapter stuff
from scout.adapter.mongo import MongoAdapter
from scout.adapter.client import get_connection
from pymongo.errors import (ConnectionFailure, ServerSelectionTimeoutError)

# Import the resources to setup scout
from scout.resources import (hgnc_path, exac_path)

from scout.resources import transcripts37_path as transcripts37_path
from scout.resources import transcripts38_path as transcripts38_path

### Import demo files ###
# Resources
from scout.demo.resources import (
    hgnc_reduced_path, exac_reduced_path, transcripts37_reduced_path, transcripts38_reduced_path, 
    mim2gene_reduced_path, genemap2_reduced_path, hpogenes_reduced_path, hpo_to_genes_reduced_path,
    hpoterms_reduced_path, hpo_phenotype_to_terms_reduced_path, madeline_path)

# Gene panel
from scout.demo import (panel_path, clinical_snv_path, clinical_sv_path,
                        research_snv_path, research_sv_path)

# Case files
from scout.demo import load_path

# Import the functions to setup scout
from scout.parse.panel import parse_gene_panel

from scout.build import (build_institute, build_case, build_panel, build_variant)

from scout.load import (load_hgnc_genes, load_hpo, load_scout)

from scout.utils.handle import get_file_handle

from scout.utils.link import link_genes

from scout.utils.requests import (fetch_mim_files, fetch_hpo_genes)

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
    """Setup a scout database"""
    LOG.info("Running scout setup database")

    # Fetch the omim information
    api_key = api_key or context.obj.get('omim_api_key')
    if not api_key:
        LOG.warning("Please provide a omim api key to load the omim gene panel")
        context.abort()

    try:
        mim_files = fetch_mim_files(api_key, mim2genes=True, morbidmap=True, genemap2=True)
    except Exception as err:
        LOG.warning(err)
        context.abort()
    
    # for fn in mim_files:
    #     click.echo("{0}: {1}".format(fn, type(mim_files[fn])))
    #
    # context.abort()
    
    institute_name = institute_name or context.obj['institute_name']
    user_name = user_name or context.obj['user_name']
    user_mail = user_mail or context.obj['user_mail']

    adapter = context.obj['adapter']

    LOG.info("Deleting previous database")
    for collection_name in adapter.db.collection_names():
        if not collection_name.startswith('system'):
            LOG.info("Deleting collection %s", collection_name)
            adapter.db.drop_collection(collection_name)
    LOG.info("Database deleted")

    LOG.info("Setting up database %s", context.obj['mongodb'])

    # Build a institute with id institute_name
    institute_obj = build_institute(
        internal_id=institute_name,
        display_name=institute_name,
        sanger_recipients=[user_mail]
    )

    # Add the institute to database
    adapter.add_institute(institute_obj)

    # Build a user obj
    user_obj = dict(
                _id=user_mail,
                email=user_mail,
                name=user_name,
                roles=['admin'],
                institutes=[institute_name]
            )

    adapter.add_user(user_obj)
    
    # Fetch the genes to hpo information
    hpo_genes = fetch_hpo_genes()
    
    # Load the genes and transcripts
    genes37 = link_genes(
        ensembl_lines=get_file_handle(transcripts37_path),
        hgnc_lines=get_file_handle(hgnc_path),
        exac_lines=get_file_handle(exac_path),
        mim2gene_lines=mim_files['mim2genes'],
        genemap_lines=mim_files['genemap2'],
        hpo_lines=hpo_genes,
    )

    load_hgnc_genes(adapter, genes37, build='37')

    genes38 = link_genes(
        ensembl_lines=get_file_handle(transcripts38_path),
        hgnc_lines=get_file_handle(hgnc_path),
        exac_lines=get_file_handle(exac_path),
        mim2gene_lines=mim_files['mim2genes'],
        genemap_lines=mim_files['genemap2'],
        hpo_lines=hpo_genes,
    )

    load_hgnc_genes(adapter, genes38, build='38')

    load_hpo(
        adapter=adapter,
        disease_lines=mim_files['genemap2'],
    )

    LOG.info("Creating indexes")
    
    adapter.load_indexes()

    LOG.info("Scout instance setup successful")

@click.command('demo', short_help='Setup a scout demo instance')
@click.pass_context
def demo(context):
    """Setup a scout demo instance. This instance will be populated with a
       case a gene panel and some variants.
    """
    LOG.info("Running scout setup demo")
    institute_name = context.obj['institute_name']
    user_name = context.obj['user_name']
    user_mail = context.obj['user_mail']

    adapter = context.obj['adapter']

    LOG.info("Setting up database %s", context.obj['mongodb'])
    LOG.info("Deleting previous database")
    for collection_name in adapter.db.collection_names():
        LOG.info("Deleting collection %s", collection_name)
        adapter.db.drop_collection(collection_name)
    LOG.info("Database deleted")

    # Build a institute with id institute_name
    institute_obj = build_institute(
        internal_id=institute_name,
        display_name=institute_name,
        sanger_recipients=[user_mail]
    )

    # Add the institute to database
    adapter.add_institute(institute_obj)

    # Build a user obj
    user_obj = dict(
                _id=user_mail,
                email=user_mail,
                name=user_name,
                roles=['admin'],
                institutes=[institute_name]
            )

    adapter.add_user(user_obj)

    # Load the genes and transcripts
    LOG.info("Loading hgnc genes from %s", hgnc_reduced_path)
    hgnc_handle = get_file_handle(hgnc_reduced_path)
    hgnc38 = get_file_handle(hgnc_reduced_path)
    
    LOG.info("Loading exac genes from %s", exac_reduced_path)
    exac_handle = get_file_handle(exac_reduced_path)
    exac38 = get_file_handle(exac_reduced_path)
    
    LOG.info("Loading mim2gene info from %s", mim2gene_reduced_path)
    mim2gene_handle = get_file_handle(mim2gene_reduced_path)
    mim2gene38 = get_file_handle(mim2gene_reduced_path)
    
    LOG.info("Loading genemap info from %s", genemap2_reduced_path)
    genemap_handle = get_file_handle(genemap2_reduced_path)
    genemap38 = get_file_handle(genemap2_reduced_path)
    
    LOG.info("Loading hpo gene info from %s", hpogenes_reduced_path)
    hpo_genes_handle = get_file_handle(hpogenes_reduced_path)
    hpo_to_genes_handle = get_file_handle(hpo_to_genes_reduced_path)
    hpogenes38 = get_file_handle(hpogenes_reduced_path)
    LOG.info("Loading hpo disease info from %s", hpo_phenotype_to_terms_reduced_path)
    hpo_disease_handle = get_file_handle(hpo_phenotype_to_terms_reduced_path)
    LOG.info("Loading hpo terms from %s", hpoterms_reduced_path)
    hpo_terms_handle = get_file_handle(hpoterms_reduced_path)
    
    LOG.info("Loading omim disease info from %s", genemap2_reduced_path)
    disease_handle = get_file_handle(genemap2_reduced_path)
    
    LOG.info("Loading transcripts build 37 info from %s", transcripts37_reduced_path)
    transcripts37_handle = get_file_handle(transcripts37_reduced_path)
    transcripts38_handle = get_file_handle(transcripts38_reduced_path)
    

    genes37 = link_genes(
        ensembl_lines=transcripts37_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle,
        hpo_lines=hpo_genes_handle,
    )

    load_hgnc_genes(adapter, genes37, build='37')

    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        hpo_gene_lines=hpo_to_genes_handle,
        disease_lines=disease_handle,
        hpo_disease_lines=hpo_disease_handle
    )

    adapter.load_panel(
        path=panel_path, 
        institute='cust000', 
        panel_id='panel1', 
        date=datetime.datetime.now(), 
        panel_type='clinical', 
        version=1.0, 
        display_name='Test panel'
    )

    case_handle = get_file_handle(load_path)
    case_data = yaml.load(case_handle)
    
    adapter.load_case(case_data)

    LOG.info("Creating indexes")

    adapter.load_indexes()

    LOG.info("Scout demo instance setup successful")

from scout.demo.resources.generate_test_data import (generate_hgnc, generate_genemap2, generate_mim2genes, 
generate_exac_genes, generate_ensembl_genes, generate_ensembl_transcripts, generate_hpo_files)
from scout.demo import panel_path

from scout.parse.panel import parse_gene_panel

# @click.group()
@click.command()
@click.pass_context
def setup(context):
    """
    Setup scout instances.
    """

    context.obj['institute_name'] = 'cust000'
    context.obj['user_name'] = 'Clark Kent'
    context.obj['user_mail'] = 'clark.kent@mail.com'

    if context.invoked_subcommand == 'demo':
        # Update context.obj settings here
        LOG.info("Change database name to scout-demo")
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

