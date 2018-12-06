# -*- coding: UTF-8 -*-

import logging
import requests
import json
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)

def mme_update(matchmaker_url, update_action, json_patient, token):
    """ Add a patient to matchmaker by posting a request

        Args:
            matchmaker_url(str): url of a matchmaker server
            update_action(str): 'add' or 'delete' to either add or delete a patient
            json_patient: a patient object as in https://github.com/ga4gh/mme-apis or an ID(str)
            token(str): authorization token

        Returns:
            json_response: a json-formatted server response
    """

    # create request headers
    headers = Headers()
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/vnd.ga4gh.matchmaker.v1.0+json', "X-Auth-Token": token}

    json_response = None
    data = {}
    method = None
    url = '/'.join([matchmaker_url, 'patient', update_action])

    if update_action == 'add':
        data["patient"] = json_patient
        method = 'POST'
    else: #delete a patient
        data["id"] = json_patient
        method = 'DELETE'
    try:
        LOG.info('sending HTTP request to server: {0}, data: {1}'.format(url, data))
        appo = json.dumps(data)
        # send request and get response from server
        server_return = requests.request(
            method = method,
            url = url,
            headers = headers,
            data = json.dumps(data)
        )
        json_response = None

        # workaround to take into account a malformed json response from matchmaker server:
        try:
            json_response = server_return.json()
        except Exception as json_exp:
            json_response = server_return.text

        LOG.info('server returns the following response: {}'.format(json_response))
    except Exception as err:
        LOG.info('An error occurred while sending HTTP request to server ({})'.format(err))
        json_response = err

    return json_response
