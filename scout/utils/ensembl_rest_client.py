# -*- coding: UTF-8 -*-
import json
import logging
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LOG = logging.getLogger(__name__)

SERVER_37 = 'https://grch37.rest.ensembl.org'
SERVER_38 = 'http://rest.ensembl.org/'
HEADERS = {'Content-type':'application/json'}
BIOMART =  "http://www.ensembl.org/biomart/martservice?query="

PING_ENDPOINT = 'info/ping'

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
        """ping ensembl

        Accepts:
            server(str): default is 'https://grch37.rest.ensembl.org'

        Returns:
            data(dict): dictionary from json response
        """
        url = '/'.join([server, PING_ENDPOINT])
        data = self.send_request(url)
        return data

    def use_api(self, endpoint, params=None):
        """Sends a request to the Ensembl REST API and returns response data from the service

        Accepts:
            endpoint(str): one of the GET endpoints defined for https://rest.ensembl.org/
            params(dict): dictionary of request parameters

        Returns:
            data(dict): dictionary from json response
        """
        if endpoint is None:
            LOG.info('Error: no endpoint specified for Ensembl REST API request.')
            return
        if params:
            endpoint += '?' + urlencode(params)

        url = ''.join([ self.server, endpoint])
        LOG.info('Using Ensembl API with the url:{}'.format(url))
        data = self.send_request(url)
        return data

    def send_request(self, url):
        """Sends the actual request to the server and returns the response

        Accepts:
            url(str): ex. https://rest.ensembl.org/overlap/id/ENSG00000157764?feature=transcript

        Returns:
            data(dict): dictionary from json response
        """
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

    def create_biomart_xml(self, filters, attributes):
        """Convert biomart query params into biomart xml query

        Accepts:
            filters(list): a list of tuples with filter name and values (ex: ('chromosome_name' : [1,2,'X']) )
            attributes(list): a list of attributes

        Returns:
            xml: a query xml file

        """
        filter_lines = [ self.xml_filter(filter[0], filter[1]) for filter in filters]
        attribute_lines = [ self.xml_attribute(attr_name) for attr_name in attributes ]
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE Query>
        <Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

        	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
                {0}
                {1}
        	</Dataset>
        </Query>""".format( filter_lines, attribute_lines)

        return xml

    def xml_filter(self, name, value):
        """Creates a filter line for the biomart xml document

        Accepts:
            name(str): filter name
            value(str or list): filter value

        Returns:
            formatted_line(str): formatted xml line
        """
        formatted_line = ""
        if type(value) == list:
            formatted_line='<Filter name = "{0}" value = "{1}"/>'.format(name, ','.join(str(value)))
        else:
            formatted_line='<Filter name = "{0}" value = "{1}"/>'.format(name, value)
        return formatted_line

    def xml_attribute(self, name):
        """Creates an attribute line for the biomart xml document

        Accepts:
            name(str): attribute name

        Returns:
            formatted_line(str): formatted xml line
        """
        formatted_line = '<Attribute name = "{}" />'.format(name)
        return formatted_line
