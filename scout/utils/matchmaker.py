# -*- coding: UTF-8 -*-
import logging
import requests
import json
import datetime;
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)

def sample_matches(mme_base_url, token, mme_sample_id):
    """Get all MatchMaker matches for a sample with a given id.

    Args:
        mme_base_url(str): base URL of MME service
        token(str): MME server authorization token
        mme_sample_id(str): the id of a sample in MatchMaker database

    Returns:
        json_response(dict). Example:
            { 'matches' : [ {match_obj1}, {match_obj2}, ..] }
    """

    json_response = None
    url = ''.join([mme_base_url, '/matches/', mme_sample_id])
    headers = Headers()
    headers = { 'X-Auth-Token': token}
    method = 'GET'

    try:
        LOG.info('Getting matches for patient {} from matchmaker server..'.format(mme_sample_id))
        # send GET request
        resp = requests.request(
            method = method,
            url = url,
            headers = headers,
            data = { 'timestamp' : datetime.datetime.now().timestamp()} #sending data so response is not cached
        )
        json_response = resp.json()
        json_response['status_code'] = resp.status_code

    except Exception as err:
        LOG.info('An error occurred while sending HTTP request to server ({})'.format(err))
        json_response = {
            'message' : str(err)
        }
    return json_response
