# -*- coding: UTF-8 -*-
import logging
import requests
import json
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)

def mme_update(mme_base_url, update_action, patient, token, content_type=None):
    """Add or remove a patient from MatchMaker server

    Args:
        mme_base_url(str): base URL of MME service
        update_action(str): 'add' or 'delete' to either add or delete a patient
        patient: a patient object (if update_action is 'add') or an id(str)
        token(str): MME server authorization token
        content_type(str): MME request Content-Type

    Returns:
        json_response: a json-formatted server response
    """
    method = None
    url = None
    headers = Headers()
    data = {}
    if update_action == 'add':
        url = ''.join([mme_base_url, '/patient/add'])
        headers = {
                'Content-Type': content_type,
                'Accept': 'application/json',
                'X-Auth-Token': token
            }
        method = 'POST'
        data["patient"] = patient

    elif update_action == 'delete':
        url = ''.join([mme_base_url, '/patient/delete/', patient])
        headers = {'Accept':'application/json',"X-Auth-Token": token}
        method = 'DELETE'

    try:
        LOG.info('sending {} request to matchmaker server..'.format(update_action.upper()))
        # send request
        resp = requests.request(
            method = method,
            url = url,
            headers = headers,
            data = json.dumps(data) #not really required for DELETE
        )
        json_response = resp.json()
        json_response['status_code'] = resp.status_code

    except Exception as err:
        LOG.info('An error occurred while sending HTTP request to server ({})'.format(err))
        json_response = {
            'message' : str(err)
        }

    return json_response
