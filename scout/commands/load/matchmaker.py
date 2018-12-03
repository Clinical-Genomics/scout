# -*- coding: utf-8 -*-
import logging
import click
import requests

from scout.load.matchmaker import matchbox_add
from scout.parse.mme import mme_patients

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
    help='url of a running matchbox instance',
    default='http://localhost:9020'
)
@click.option('--token',
    type=click.STRING,
    nargs=1,
    required=True,
    help='matchbox authorization token',
)


@click.pass_context
def mme_patient(context, json, token,  mme_url):
    """Load one or more patients to the database

        Args:
            json(str): Path to a json file containing patient data

            mme_url(str) : URL of the matchmaker instance the patients should be saved to.
                If this is provided the patients will be included in matchbox by sending a POST
                request to the server, triggering in turn a search of the same patients over the connected nodes.

        Returns:
            BOOOOH!!!!

    """
    LOG.info('Save one or more patients to matchbox and query connected nodes')
    mme_patient_list = []
    try:
        mme_patient_list = mme_patients(json) # a list of MME patient dictionaries
    except Exception as err:
        LOG.warning("Something went wrong while parsing patient file: {}".format(err))
        context.abort()

    response = [] # a list of matchbox server responses, one for each patient

    for patient in mme_patient_list:
        resp = matchbox_add(matchbox_url=mme_url, json_patient=patient, token=token)
        LOG.info(str(resp))


    return None
