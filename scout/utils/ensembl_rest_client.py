# -*- coding: UTF-8 -*-
import json
import logging
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import urlencode

LOG = logging.getLogger(__name__)

SERVER_37 = 'https://grch37.rest.ensembl.org'
SERVER_38 = 'http://rest.ensembl.org/'
HEADERS = {'Content-type':'application/json'}

PING_ENDPOINT = 'info/ping'
#EXON = "/overlap/region/human/7:140424943-140624564?feature=gene;feature=transcript;feature=cds;feature=exon"

class EnsemblRestClient:
    """A class handling requests and responses to and from the Ensembl REST APIs.
    Endpoints for human build 37: https://grch37.rest.ensembl.org
    Endpoints for human build 38: http://rest.ensembl.org/
    Documentation: https://github.com/Ensembl/ensembl-rest/wiki
    doi:10.1093/bioinformatics/btu613
    """

    def __init__(self, build='37'):
        if build == '38':
            self.server = SERVER_38
        else:
            self.server = SERVER_37

    def ping_server(self, server=SERVER_37):
        """ping the ensembl servers"""
        url = '/'.join([server, PING_ENDPOINT])
        data = self.send_request(url)
        return data

    def use_api(self, endpoint, params=None):
        """Sends a request to the Ensembl REST API and returns response data from the service"""
        if endpoint is None:
            LOG.info('Error: Ensembl REST API was invoked without providing params.')
            return

        if params:
            endpoint += '?' + urlencode(params)

        return endpoint

    def send_request(self, url):
        """Sends the actual request to the server and returns the response"""

        data = {}
        try:
            request = Request(url, headers=HEADERS)
            response = urlopen(request)
            content = response.read()
            if content:
                data = json.loads(content)
        except HTTPError as e:
            LOG.info('Request failed for url {0}: Error: {1}\n'.format(url, e))
            data = e
        except ValueError as e:
            LOG.info('Request failed for url {0}: Error: {1}\n'.format(url, e))
            data = e
        return data
