# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from invoke import run, task
from invoke.util import log
from codecs import open

import yaml
from mongoengine import connect

from scout.adapter import MongoAdapter
from scout.models import (User, Whitelist, Institute)
from scout.load import (load_scout, load_hgnc_genes, load_hpo, load_institute)
from scout import logger
from scout.log import init_log
from scout.utils.handle import get_file_handle
from scout.utils.link import link_genes

hgnc_path = "tests/fixtures/resources/hgnc_reduced_set.txt"
ensembl_transcript_path = "tests/fixtures/resources/ensembl_transcripts_reduced.txt"
exac_genes_path = "tests/fixtures/resources/forweb_cleaned_exac_r03_march16_z_data_pLI_reduced.txt"
hpo_genes_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype_reduced.txt"
hpo_terms_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes_reduced.txt"
hpo_disease_path = "tests/fixtures/resources/ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes_reduced.txt"

init_log(logger, loglevel='INFO')

@task
def setup_test(context, email, name="Paul Anderson"):
    """docstring for setup"""
    db_name = 'test-database'
    adapter = MongoAdapter()
    adapter.connect_to_database(database=db_name)
    adapter.drop_database()

    institute_info = {
        'internal_id': 'cust000',
        'display_name': 'test-institute',
        'sanger_recipients': [email]
    }
    
    load_institute(
        adapter=adapter,
        internal_id=institute_info['internal_id'], 
        display_name=institute_info['display_name'], 
        sanger_recipients=institute_info['sanger_recipients']
    )
    
    institute = adapter.institute(institute_id=institute_info['internal_id'])
    # create user to test login
    Whitelist(email=email).save()
    user = User(email=email,
                name=' '.join(email.split('@')[0].split('.')),
                roles=['admin'],
                institutes=[institute])
    user.save()

    # create user to test without login
    Whitelist(email='paul.anderson@magnolia.com')
    new_user = User(email='paul.anderson@magnolia.com',
                    name='Paul T. Anderson',
                    roles=['admin'],
                    institutes=[institute])
    new_user.save()

    hgnc_handle = get_file_handle(hgnc_path)
    ensembl_handle = get_file_handle(ensembl_transcript_path)
    exac_handle = get_file_handle(exac_genes_path)
    hpo_genes_handle = get_file_handle(hpo_genes_path)
    hpo_terms_handle = get_file_handle(hpo_terms_path)
    hpo_disease_handle = get_file_handle(hpo_disease_path)

    genes = link_genes(
        ensembl_lines=ensembl_handle, 
        hgnc_lines=hgnc_handle, 
        exac_lines=exac_handle, 
        hpo_lines=hpo_genes_handle
    )
    # Load the genes and transcripts
    load_hgnc_genes(
        adapter=adapter,
        genes=genes,
    )

    # Load the hpo terms and diseases
    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        disease_lines=hpo_disease_handle
    )
    
    ## TODO load some gene panels
    ## TODO update the config files
    
    for index in [1, 2]:
        with open("tests/fixtures/config{}.yaml".format(index)) as in_handle:
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
