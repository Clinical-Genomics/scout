# -*- coding: utf-8 -*-
import logging
import click
import json
import requests

from scout.update.matchmaker import mme_update
from scout.parse.mme import mme_patients, phenotype_features, omim_disorders, genomic_features

LOG = logging.getLogger(__name__)

@click.command('mme_patient', short_help='Load one or more patients to MatchMaker Exchange')
# the email of a valid user in scout. Name will be collected for the user as well since
# contact info is mandatory to insert patients into MatchMaker Exchange
@click.option('-email',
    type=click.STRING,
    nargs=1,
    required=True,
    help='email of the scout user to include in MME contact info'
)
@click.option('-json_file',
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
def mme_patient(context, email, json_file, case_id, token, mme_url):
    """Load one or more patients to MatchMaker Exchange

        Args:
            json_file(str): Path to a json file containing patient data

            case_id(str): a scout case ID

            mme_url(str) : URL of the matchmaker instance the patients should be saved to.
                When this is provided the patients will be included in its database by sending a POST
                request to the server, triggering in turn a search of the same patients over the connected nodes.

    """

    LOG.info('Save one or more patients to matchmaker and query all connected nodes')
    mme_patient_list = []

    # collect contact info to include in patient data
    adapter = context.obj['adapter']
    user_obj = adapter.user(email=email)
    if user_obj is None:
        LOG.info("could't find any user with email '{} in scout database!'".format('email'))
        context.abort()
    contact_info = {
        'name' : user_obj['name'],
        'href' : user_obj['email'],
        'institution' : 'Customer of SciLifeLab Stockholm, Sweden.'
    }

    # if patients to include in matchmaker are passed by json file
    if json_file:
        try:
            mme_patient_list = mme_patients(json_file) # a list of MME patient dictionaries
        except Exception as err:
            LOG.warning("Something went wrong while parsing patient file: {}".format(err))
            context.abort()

    # else if patients are already stored inside scout database
    elif case_id:
        # collect data for each affected subject of a provided case
        case_obj = adapter.case(case_id=case_id)
        if case_obj is None:
            LOG.info('No case with id "{}"'.format(case_id))
            context.abort()

        # collect HPO phenotype terms (if available) for this case
        features = phenotype_features(case_obj)
        LOG.info('collected phenotypes for this case:{}'.format(features))

        # collect OMIM disorders (if available) for this case
        disorders = omim_disorders(case_obj)
        LOG.info('collected disorders for this case:{}'.format(disorders))

        # collect each affected individual and its genomic features for this case
        for individual in case_obj.get('individuals'):
            if individual['phenotype'] == 2: # affected
                mme_patient = {}
                mme_patient['contact'] = contact_info
                mme_patient['id'] = '.'.join([case_obj['_id'], individual.get('individual_id')]) # This is a required field form MME
                mme_patient['label'] = '.'.join([case_obj['display_name'], individual.get('display_name')])
                mme_patient['features'] = features
                mme_patient['disorders'] = disorders

                # get all snv variants for this specific individual:
                individual_variants = list(adapter.case_individual_snv_variants(case_id, individual.get('display_name')))
                LOG.info('number of variants found for affected individual {0}: {1}'.format(case_obj['display_name'], len(individual_variants )))

                # parse variants to obtain MatchMaker-like variant objects (genomic features)
                mme_patient['genomicFeatures'] = genomic_features(adapter, scout_variants=individual_variants, sample_name=individual.get('display_name'), build=case_obj.get('genome_build'))

                if individual['sex'] == '1':
                    mme_patient['sex'] = 'MALE'
                else:
                    mme_patient['sex'] = 'FEMALE'

                mme_patient_list.append(mme_patient)

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
