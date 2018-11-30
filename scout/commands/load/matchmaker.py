# -*- coding: utf-8 -*-
import logging
import click

from scout.parse.mme import validate_mme_json

LOG = logging.getLogger(__name__)

@click.command('mme_patient', short_help='Load one or more patients to MatchMaker Exchange')
@click.option('--json',
    type=click.Path(exists=True),
    nargs=1,
    required=True,
    help='path to json file containing one or more patients'
)
@click.option('--mme_url',
    type=click.STRING,
    nargs=1,
    required=False,
    help='send patients to matchbox URL and search connected nodes.'
)
@click.option('--mme_uri',
    type=click.STRING,
    nargs=1,
    required=False,
    help='save patients to mongodb database without querying connected nodes (example: mongodb://mboxuser:mboxpassword@127.0.0.1:27017/cgmatchbox)',
    default='mongodb://mboxuser:mboxpassword@127.0.0.1:27017/cgmatchbox'
)

@click.pass_context
def mme_patient(context, json, mme_url=None, mme_uri=None):
    """Load one or more patients to the database

    Args:
        json(str): Path to a json file containing patient data

        mme_url(str) : URL of the matchmaker instance the patients should be saved to.
            If this is provided the patients will be included in matchbox by sending a POST
            request to the server, triggering in turn a search of the same patients over the connected nodes.

        mme_uri(str): Connect URI to mongo database containing Matchbox collections
            if this is provided, patients will be saved to database without querying
            the connected nodes.
    """
    LOG.info('Save patients to matchbox')
    appo = validate_mme_json(json)





    # if patient(s) should be saved by POST request to server:
    if mme_url:
        LOG.info('POST request the server with one or more patients')
    # if patient(s) should be saved directly to database, without querying other MME nodes:
    elif mme_uri:
        LOG.info('insert patients to database')
    else:
        LOG.info('return error')
