import logging
import requests
import json
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)

def matchbox_add(matchbox_url, json_patient, token):
    """ Add a patient to matchbox by posting a request

        Args:
            matchbox_url(str): url of matchbox server
            patient(dict): a patient object as in https://github.com/ga4gh/mme-apis
            auth_token(str): authorization token

        Returns:
            json_response: a json-formatted server response
    """

    # create request headers
    headers = Headers()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/vnd.ga4gh.matchmaker.v1.0+json', "X-Auth-Token": token}

    json_response = None
    patient = {
        "patient" : json_patient
    }
    LOG.info('patient:{}'.format(patient))
    try:
        LOG.info('sending HTTP request to server: {}'.format(matchbox_url))
        server_return = requests.request(
            method = 'POST',
            url = '/'.join([matchbox_url, 'patient', 'add']),
            headers = headers,
            data = json.dumps(patient)
        )
        json_response = server_return.json()
        LOG.info('server returns the following response: {}'.format(json_response))
    except Exception as err:
        LOG.info('An error occurred while sending HTTP request to server ({})'.format(err))
        json_response = err

    return json_response
