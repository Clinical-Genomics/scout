#!/usr/bin/env python
# encoding: utf-8
"""
init.py

Initialize a scout instance with a institute, a user, genes, transcripts,
hpo terms and hpo diseases

Created by Måns Magnusson on 2016-05-11.
Copyright (c) 2016 ScoutTeam__. All rights reserved.

"""

import logging

import click

from scout.resources import (hgnc_path, exac_path, mim2gene_path,
                             genemap2_path, hpogenes_path, hpoterms_path,
                             hpodisease_path)

from scout.resources import transcripts37_path as transcripts_path

from scout.build import build_institute

from scout.load import (load_hgnc_genes, load_hpo)

from scout.utils.handle import get_file_handle
from scout.utils.link import link_genes

logger = logging.getLogger(__name__)


@click.command('init', short_help='Initialize a scout instance')
@click.option('-i', '--institute-name', default='test')
@click.option('-u', '--user-name', default='Clark Kent')
@click.option('-m', '--user-mail', default='clark.kent@mail.com')
@click.pass_context
def init(ctx, institute_name, user_name, user_mail):
    """
    Setup a working scout instance.
    """
    logger.info("Running scout init")

    adapter = ctx.obj['adapter']

    logger.info("Deleting previous database")
    for collection_name in adapter.db.collection_names():
        logger.info("Deleting collection %s", collection_name)
        adapter.db.drop_collection(collection_name)
    logger.info("Database deleted")

    institute_obj = build_institute(
        internal_id=institute_name,
        display_name=institute_name,
        sanger_recipients=[user_mail]
    )

    adapter.add_institute(institute_obj)

    adapter.add_whitelist(
        email=user_mail,
        institutes=[institute_name]
    )

    user_obj = dict(email=user_mail,
                name=user_name,
                roles=['admin'],
                institutes=[institute_name])
    adapter.add_user(user_obj)

    # Load the genes and transcripts
    logger.info("Loading hgnc file from {0}".format(hgnc_path))
    hgnc_handle = get_file_handle(hgnc_path)

    logger.info("Loading ensembl transcript file from {0}".format(
                transcripts_path))
    transcripts_handle = get_file_handle(transcripts_path)

    logger.info("Loading exac gene file from {0}".format(
                exac_path))
    exac_handle = get_file_handle(exac_path)

    logger.info("Loading HPO gene file from {0}".format(
                hpogenes_path))
    hpo_genes_handle = get_file_handle(hpogenes_path)

    logger.info("Loading mim2gene file from {0}".format(
                hpogenes_path))
    mim2gene_handle = get_file_handle(mim2gene_path)

    logger.info("Loading genemap file from {0}".format(
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

    logger.info("Loading hpo terms from file {0}".format(hpoterms_path))
    logger.info("Loading hpo disease terms from file {0}".format(hpodisease_path))

    hpo_terms_handle = get_file_handle(hpoterms_path)
    disease_handle = get_file_handle(genemap2_path)

    load_hpo(
        adapter=adapter,
        hpo_lines=hpo_terms_handle,
        disease_lines=disease_handle
    )

    logger.info("Scout instance setup successful")
