# -*- coding: UTF-8 -*-
import logging
import requests
import json
import datetime;
from werkzeug.datastructures import Headers

LOG = logging.getLogger(__name__)

def matchmaker_request(url, token, method, content_type=None, accept=None, data=None):
    """Send a request to MatchMaker and return its response

    Args:
        url(str): url to send request to
        token(str): MME server authorization token
        method(str): 'GET', 'POST' or 'DELETE'
        content_type(str): MME request Content-Type
        accept(str): accepted response
        data(dict): eventual data to send in request

    Returns:
        json_response(dict): server response
    """
    headers = Headers()
    headers = { 'X-Auth-Token': token}
    if content_type:
        headers['Content-Type'] = content_type
    if accept:
        headers['Accept'] = accept

    #sending data anyway so response will not be cached
    req_data = data or {'timestamp' : datetime.datetime.now().timestamp()}
    json_response = None
    try:
        LOG.info('Sending {} request to MME url {}. Data sent: {}'.format(
            method, url, req_data))
        resp = requests.request(
            method = method,
            url = url,
            headers = headers,
            data = json.dumps(req_data)
        )
        json_response = resp.json()
        LOG.info('MME server response was:{}'.format(json_response))
        json_response['status_code'] = resp.status_code

    except Exception as err:
        LOG.info('An error occurred while sending HTTP request to server ({})'.format(err))
        json_response = {
            'message' : str(err)
        }
    return json_response















def mme_nodes(mme_base_url, token):
    """Return the available MatchMaker nodes

    Args:
        mme_base_url(str): base URL of MME service
        token(str): MME server authorization token

    Returns:
        nodes(list): a list of node disctionaries
    """
    nodes = []
    if not mme_base_url or not token:
        return nodes
    url = ''.join([mme_base_url, '/nodes'])
    headers = Headers()
    headers = { 'X-Auth-Token': token}
    method = 'GET'
    try:
        LOG.info('Getting available external matchmaker nodes.')
        # send GET request
        resp = requests.request(
            method = method,
            url = url,
            headers = headers,
            data = { 'timestamp' : datetime.datetime.now().timestamp()} #sending data so response is not cached
        )
        nodes = resp.json()
    except Exception as err:
        LOG.info('An error occurred while getting available MME nodes:{}'.format(err))

    return nodes

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
