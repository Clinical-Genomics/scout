# -*- coding: UTF-8 -*-
import json
import logging
import requests
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LOG = logging.getLogger(__name__)

HEADERS = {'Content-type':'application/json'}
RESTAPI_37 = 'http://grch37.rest.ensembl.org'
RESTAPI_38 = 'http://rest.ensembl.org/'
PING_ENDPOINT = 'info/ping'

BIOMART_37 =  "http://grch37.ensembl.org/biomart/martservice?query="
BIOMART_38 =  "http://ensembl.org/biomart/martservice?query="

class EnsemblRestApiClient:
    """A class handling requests and responses to and from the Ensembl REST APIs.
    Endpoints for human build 37: https://grch37.rest.ensembl.org
    Endpoints for human build 38: http://rest.ensembl.org/
    Documentation: https://github.com/Ensembl/ensembl-rest/wiki
    doi:10.1093/bioinformatics/btu613
    """

    def __init__(self, build='37'):
        if build == '38':
            self.server = RESTAPI_38
        else:
            self.server = RESTAPI_37

    def ping_server(self, server=RESTAPI_38):
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
        LOG.info('Using Ensembl API with the following url:{}'.format(url))
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


class EnsemblBiomartClient:

    def __init__(self, build='37'):
        if build == '38':
            self.server = BIOMART_38
        else:
            self.server = BIOMART_37
        LOG.info("Setting up ensembl biomart client with server %s", self.server)

    def query_service(self, xml=None, filters=None, attributes=None):
        """Query the Ensembl biomart service and yield the resulting lines

        Accepts:
            xml(str): an xml formatted query, as described here:
                https://grch37.ensembl.org/info/data/biomart/biomart_perl_api.html
            filters(dict): A dictionary with the filters to use and their value
            attributes(list): A list with attributes to use
        
        Yields:
            biomartline 
        """
        if not xml:
            xml = self.create_biomart_xml(filters, attributes)

        url = ''.join([self.server, xml])
        try:
            with requests.get(url, stream=True) as r:
                for line in r.iter_lines():
                    yield line.decode('utf-8')
        except Exception as ex:
            LOG.info('Error downloading data from biomart: {}'.format(ex))
            raise ex

    def create_biomart_xml(self, filters=None, attributes=None):
        """Convert biomart query params into biomart xml query

        Accepts:
            filters(dict): keys are filter names and values are filter values
            attributes(list): a list of attributes

        Returns:
            xml: a query xml file

        """
        filters = filters or {}
        attributes = attributes or []
        filter_lines = self.xml_filters(filters)
        attribute_lines = self.xml_attributes(attributes)
        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<!DOCTYPE Query>',
            '<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows'\
            ' = "0" count = "" datasetConfigVersion = "0.6" completionStamp = "1">',
            '',
            '\t<Dataset name = "hsapiens_gene_ensembl" interface = "default" >',
        ]
        for line in filter_lines:
            xml_lines.append('\t\t'+line)
        for line in attribute_lines:
            xml_lines.append('\t\t'+line)
        xml_lines += [
            '\t</Dataset>',
            '</Query>'
        ]

        return '\n'.join(xml_lines)

    def xml_filters(self, filters):
        """Creates a filter line for the biomart xml document

        Accepts:
            filters(dict): keys are filter names and values are filter values

        Returns:
            formatted_lines(list[str]): List of formatted xml filter lines
        """
        formatted_lines = []
        for filter_name in filters:
            value = filters[filter_name]
            if isinstance(value, str):
                formatted_lines.append('<Filter name = "{0}" value = "{1}"/>'.format(
                                    filter_name, value))
            else:
                formatted_lines.append('<Filter name = "{0}" value = "{1}"/>'.format(
                                    filter_name, ','.join(value)))
                
        return formatted_lines

    def xml_attributes(self, attributes):
        """Creates an attribute line for the biomart xml document

        Accepts:
            attributes(list): attribute names

        Returns:
            formatted_lines(list(str)): list of formatted xml attribute lines
        """
        formatted_lines = []
        for attr in attributes:
            formatted_lines.append('<Attribute name = "{}" />'.format(attr))
        return formatted_lines

