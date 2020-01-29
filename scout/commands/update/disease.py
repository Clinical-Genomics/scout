#!/usr/bin/env python
# encoding: utf-8
"""
update/disease.py

Update the disease terms in database

Created by Måns Magnusson on 2017-04-03.
Copyright (c) 2017 __MoonsoInc__. All rights reserved.
"""

import logging

import click
from flask.cli import current_app, with_appcontext

from scout.load.hpo import load_disease_terms
from scout.server.extensions import store
from scout.utils.handle import get_file_handle
from scout.utils.scout_requests import fetch_mim_files

LOG = logging.getLogger(__name__)


@click.command("diseases", short_help="Update disease terms")
@click.option("--api-key", help="Specify the api key")
@click.option("--genemap2", type=click.Path(exists=True), help="Path to genemap2 file")
@with_appcontext
def diseases(api_key, genemap2):
    """
    Update disease terms in mongo database.

    If no file is specified the file will be fetched from OMIM with the api-key
    """
    adapter = store

    # Fetch the omim information
    api_key = api_key or current_app.config.get("OMIM_API_KEY")
    if genemap2:
        genemap_lines = get_file_handle(genemap2)

    else:
        if not api_key:
            LOG.warning("Please provide a omim api key to load the omim gene panel")
            raise click.Abort()

        try:
            mim_files = fetch_mim_files(api_key, genemap2=True)
            genemap_lines = mim_files["genemap2"]
        except Exception as err:
            LOG.warning(err)
            raise click.Abort()

    LOG.info("Dropping DiseaseTerms")
    adapter.disease_term_collection.drop()
    LOG.debug("DiseaseTerms dropped")
    load_disease_terms(adapter=adapter, genemap_lines=genemap_lines)

    LOG.info("Successfully loaded all disease terms")
