# -*- coding: utf-8 -*-
import logging
import click
import requests

from scout.update.matchmaker import mme_update
from scout.parse.mme import mme_patients

LOG = logging.getLogger(__name__)

@click.command('mme_patient', short_help='Load one or more patients to MatchMaker Exchange')
@click.option('-json',
    type=click.Path(exists=True),
    nargs=1,
    required=True,
    help='path to json file containing one or more patients'
)
@click.option('-mme_url',
    type=click.STRING,
    nargs=1,
    required=False,
    help='url of a running matchmaker instance',
    default='http://localhost:9020'
)
@click.option('-token',
    type=click.STRING,
    nargs=1,
    required=True,
    help='matchmaker authorization token',
)

@click.pass_context
def mme_patient(context, json, token,  mme_url):
    """Load one or more patients to the database

        Args:
            json(str): Path to a json file containing patient data

            mme_url(str) : URL of the matchmaker instance the patients should be saved to.
                When this is provided the patients will be included in its database by sending a POST
                request to the server, triggering in turn a search of the same patients over the connected nodes.

    """

    LOG.info('Save one or more patients to matchmaker and query all connected nodes')
    mme_patient_list = []
    try:
        mme_patient_list = mme_patients(json) # a list of MME patient dictionaries
    except Exception as err:
        LOG.warning("Something went wrong while parsing patient file: {}".format(err))
        context.abort()


    n_succes_response = 0
    n_inserted = 0
    n_updated = 0

    counter = 0

    for patient in mme_patient_list:
        resp = mme_update(matchmaker_url=mme_url, update_action='add', json_patient=patient, token=token)
        message = resp['message']

        if resp.get('status_code') == 200:
            n_succes_response += 1

        if message == 'insertion OK':
            n_inserted +=1
        elif 'That patient record (specifically that ID) had already been submitted in the past' in message:
            n_updated +=1
        LOG.info('Number of new patients in matchmaker:{0}, number of updated records:{1}, number of failed requests:{2}'.format(n_inserted, n_updated, (len(mme_patient_list)-n_succes_response) ))
