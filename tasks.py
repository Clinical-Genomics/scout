# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import logging
import sys

from invoke import run, task
from invoke.util import log
from codecs import open

import yaml
from scout.adapter.client import get_connection

from scout.adapter.mongo import MongoAdapter
from scout.models import (User, Whitelist, Institute)
from scout.build import build_institute
from scout.load import (load_scout, load_hgnc_genes, load_hpo, load_institute)
from scout.load.panel import load_panel
from scout import logger as base_logger
from scout.log import init_log
from scout.utils.handle import get_file_handle
from scout.utils.link import link_genes

# Variant and load files:
vcf_research_file = "tests/fixtures/643594.research.vcf"
sv_research_path = "tests/fixtures/1.SV.vcf"
vcf_clinical_file = "tests/fixtures/643594.clinical.vcf"
sv_clinical_path = "tests/fixtures/643594.clinical.SV.vcf"
ped_path = "tests/fixtures/643594.ped"
scout_yaml_config = 'tests/fixtures/643594.config.yaml'

# Panel file
panel_1_path = "tests/fixtures/gene_lists/panel_1.txt"
madeline_file = "tests/fixtures/madeline.xml"

# Resource files
hgnc_path = "tests/fixtures/resources/hgnc_reduced_set.txt"
ensembl_transcript_path = "tests/fixtures/resources/ensembl_transcripts_reduced.txt"
exac_genes_path = "tests/fixtures/resources/forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt"
hpo_genes_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype_reduced.txt"
hpo_terms_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes_reduced.txt"
hpo_disease_path = "tests/fixtures/resources/diseases_to_genes.txt"
mim2gene_path = "tests/fixtures/resources/mim2gene_reduced.txt"
genemap_path = "tests/fixtures/resources/genemap2_reduced.txt"
mimtitles_path = "tests/fixtures/resources/mimTitles_reduced.txt"

init_log(base_logger, loglevel='INFO')

log = logging.getLogger(__name__)

@task
def setup_test(context, email, name="Paul Anderson"):
    """Setup a small test database"""
    
    log.info("Running setup test database")
    
    try:
        client = get_connection()
    except ConnectionFailure:
        ctx.abort()
    
    db_name = 'test-database'
    log.info("Use database %s", db_name)
    database = client[db_name]
    adapter = MongoAdapter(database)
    
    log.info("Deleting previous database")
    for collection_name in adapter.db.collection_names():
        log.info("Deleting collection %s", collection_name)
        adapter.db.drop_collection(collection_name)
    log.info("Database deleted")

    institute_info = {
        'internal_id': 'cust000',
        'display_name': 'test-institute',
        'sanger_recipients': [email]
    }
    
    institute_obj = build_institute(
        internal_id=institute_info['internal_id'],
        display_name=institute_info['display_name'],
        sanger_recipients=institute_info['display_name']
    )
    
    adapter.add_institute(institute_obj)
    
    adapter.add_whitelist(
        email=email,
        institutes=[institute_info['internal_id']]
    )
    user_obj = dict(email=email,
                name=name,
                roles=['admin'],
                institutes=[institute_info['internal_id']]
    )
    adapter.add_user(user_obj)
    
    log.info("Loading hgnc_genes from %s", hgnc_path)
    hgnc_handle = get_file_handle(hgnc_path)
    
    log.info("Loading transcripts from %s", ensembl_transcript_path)
    ensembl_handle = get_file_handle(ensembl_transcript_path)
    
    log.info("Loading exac info from %s", exac_genes_path)
    exac_handle = get_file_handle(exac_genes_path)
    
    log.info("Loading hpo gene info from %s", hpo_genes_path)
    hpo_genes_handle = get_file_handle(hpo_genes_path)
    
    log.info("Loading terms from %s", hpo_terms_path)
    hpo_terms_handle = get_file_handle(hpo_terms_path)
    
    log.info("Loading disease info form %s", genemap_path)
    genemap_handle = get_file_handle(genemap_path)
    
    mim2gene_handle = get_file_handle(mim2gene_path)

    genes = link_genes(
        ensembl_lines=ensembl_handle,
        hgnc_lines=hgnc_handle,
        exac_lines=exac_handle,
        mim2gene_lines=mim2gene_handle,
        genemap_lines=genemap_handle, 
        hpo_lines=hpo_genes_handle,
    )
    load_hgnc_genes(adapter, genes)

    hpo_terms_handle = get_file_handle(hpo_terms_path)
    disease_handle = get_file_handle(genemap_path)

    # Load the hpo terms and diseases
    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        disease_lines=disease_handle
    )

    sys.exit()
    panel_info = {
        'date': datetime.date.today(),
        'file': panel_1_path,
        'type': 'clinical',
        'institute': 'cust000',
        'version': '1.0',
        'name': 'panel1',
        'full_name': 'Test panel',
    }

    load_panel(
        adapter=adapter,
        panel_info=panel_info
    )

    # for index in [1, 2]:
    with open(scout_yaml_config, 'r') as in_handle:
            config = yaml.load(in_handle)
    load_scout(adapter=adapter, config=config)


@task
def teardown(context):
    db_name = 'variantDatabase'
    adapter = MongoAdapter()
    adapter.connect_to_database(
        database=db_name
    )
    adapter.drop_database()


@task
def test(context):
    """test - run the test runner."""
    run('python -m pytest tests/', pty=True)


@task(name='add-user')
def add_user(context, email, name='Paul Anderson'):
    """Setup a new user for the database with a default institute."""
    connect('variantDatabase', host='localhost', port=27017)

    institute = Institute(internal_id='cust000', display_name='Clinical')
    institute.save()
    Whitelist(email=email).save()
    # create a default user
    user = User(
        email=email,
        name=name,
        roles=['admin'],
        institutes=[institute]
    )
    user.save()


@task
def clean(context):
    """clean - remove build artifacts."""
    run('rm -rf build/')
    run('rm -rf dist/')
    run('rm -rf scout.egg-info')
    run('find . -name __pycache__ -delete')
    run('find . -name *.pyc -delete')
    run('find . -name *.pyo -delete')
    run('find . -name *~ -delete')

    log.info('cleaned up')


@task
def lint(context):
    """lint - check style with flake8."""
    run('flake8 scout tests')


@task
def coverage(context):
    """coverage - check code coverage quickly with the default Python."""
    run('coverage run --source scout setup.py test')
    run('coverage report -m')
    run('coverage html')
    run('open htmlcov/index.html')

    log.info('collected test coverage stats')


@task(clean)
def publish(context, test=False):
    """publish - package and upload a release to the cheeseshop."""
    if test:
        run('python setup.py register -r test sdist upload -r test')
    else:
        run('python setup.py register bdist_wheel upload')
        run('python setup.py register sdist upload')

    log.info('published new release')


@task()
def d(context, host='0.0.0.0'):
    """Debug."""
    run("python manage.py runserver --host=%s --debug --reload" % host)
