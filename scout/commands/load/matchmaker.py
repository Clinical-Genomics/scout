# -*- coding: utf-8 -*-
import logging
import click
import requests

from scout.update.matchmaker import mme_update
from scout.export.matchmaker_patient import phenotype_features, genomic_features
from scout.parse.mme import mme_patients

LOG = logging.getLogger(__name__)

@click.command('mme_patient', short_help='Load one or more patients to MatchMaker Exchange')
@click.option('-json',
    type=click.Path(exists=True),
    nargs=1,
    required=False,
    help='path to json file containing one or more patients'
)
@click.option('-case_id',
    type=click.STRING,
    nargs=1,
    required=False,
    help='load affected patients from a scout case'
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
def mme_patient(context, json, case_id, token, mme_url):
    """Load one or more patients to the database

        Args:
            json(str): Path to a json file containing patient data

            case_id(str): a scout case ID

            mme_url(str) : URL of the matchmaker instance the patients should be saved to.
                When this is provided the patients will be included in its database by sending a POST
                request to the server, triggering in turn a search of the same patients over the connected nodes.

    """

    LOG.info('Save one or more patients to matchmaker and query all connected nodes')
    mme_patient_list = []

    # if patients to include in matchmaker are passed by json file
    if json:
        try:
            mme_patient_list = mme_patients(json) # a list of MME patient dictionaries
        except Exception as err:
            LOG.warning("Something went wrong while parsing patient file: {}".format(err))
            context.abort()

    elif case_id: # else if patients are already stored inside scout database
        # collect data for each affected subject of a provided case
        adapter = context.obj['adapter']
        case_obj = adapter.case(case_id=case_id)
        if case_obj is None:
            LOG.info('No case with id "{}"'.format(case_id))
            context.abort()

        # collect phenotype terms for this case
        features = phenotype_features(adapter, case_obj)
        LOG.info('collected phenotypes for this case:{}'.format(features))

        # collect each affected individual for a case
        # and create a matchmaker patient model for it
        for individual in case_obj.get('individuals'):
            if individual['phenotype'] == 2:
                mme_patient = {}
                mme_patient['id'] = '_'.join([case_obj['_id'], individual.get('display_name')])
                mme_patient['features'] = features

                # get all variants for this specific individual:
                individual_variants = list(adapter.case_individual_variants(case_id, individual.get('display_name')))

                LOG.info('number of variants found for affected individual {0}: {1}'.format(case_obj['display_name'], len(individual_variants )))

                # export the above variants to matchmaker-like genotype feature objects
                #mme_patient['genomicFeatures'] = genomic_features(adapter,individual_variants)



                #LOG.info((mme_patient['genomicFeatures']))



            # collect variants for affected individuals of this case
            # these will be the genomic features to include in Matchmaker
    else:
        LOG.warning('You should provide either a scout case ID or a json file!')
        context.abort()

    n_succes_response = 0
    n_inserted = 0
    n_updated = 0

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
