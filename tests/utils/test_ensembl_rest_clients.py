# -*- coding: UTF-8 -*-
import tempfile
from urllib.error import HTTPError
from urllib.parse import urlencode
from scout.utils import ensembl_rest_clients as eracs

def test_ping_ensemble_37():
    """Test ping ensembl server containing human build 37"""
    client = eracs.EnsemblRestApiClient()
    data = client.ping_server()
    assert data == {'ping':1}

def test_ping_ensemble_38():
    """Test ping ensembl server containing human build 38"""
    client = eracs.EnsemblRestApiClient(build='38')
    data = client.ping_server()
    assert data == {'ping':1}

def test_send_gene_request():
    """Test send request with correct params and endpoint"""
    url = 'https://grch37.rest.ensembl.org/overlap/id/ENSG00000103591?feature=gene'
    client = eracs.EnsemblRestApiClient()
    data = client.send_request(url)
    # get all gene for the ensembl gene, They should be a list of items
    assert data[0]['assembly_name'] == 'GRCh37'
    assert data[0]['external_name'] == 'AAGAB'
    assert data[0]['start']
    assert data[0]['end']

def test_send_request_wrong_url():
    """Successful requests are tested by other tests in this file.
       This test will trigger errors instead.
    """
    url = 'fakeyurl'
    client = eracs.EnsemblRestApiClient()
    data = client.send_request(url)
    assert type(data) == ValueError

    url = 'https://grch37.rest.ensembl.org/fakeyurl'
    data = client.send_request(url)
    assert type(data) == HTTPError

def test_use_api():
    """Test the use_api method of the EnsemblRestClient"""

    endpoint = '/overlap/id/ENSG00000157764'
    params = {
        'feature' : 'transcript'
    }
    client = eracs.EnsemblRestApiClient(build='38')

    # get all transctipts for an ensembl gene, They should be a list of items
    data = client.use_api(endpoint, params)
    assert data[0]['assembly_name'] == 'GRCh38'
    assert data[0]['feature_type'] == 'transcript'
    assert data[0]['id']
    assert data[0]['start']
    assert data[0]['strand']


def test_xml_filters():
    """test method that creates filter lines for the biomart xml file"""

    ## GIVEN a dictionary of biomart filters
    filters = {
        'string_filter' : 'string_value',
        'list_filter' : ['1','X','MT'],
    }

    client = eracs.EnsemblBiomartClient()
    xml_lines = client._xml_filters(filters)

    # make sure lines are formatted as they should
    assert '<Filter name = "{0}" value = "{1}"/>'.format('string_filter', 'string_value') in xml_lines
    assert '<Filter name = "{0}" value = "{1}"/>'.format('list_filter', '1,X,MT') in xml_lines

def test_xml_attributes():
    """test method that creates attribute lines for the biomart xml file"""

    ## Given a list of  biomart attributes
    name = ["test_name"]
    client = eracs.EnsemblBiomartClient()
    ## WHEN creating the xml attribute lines
    attribute_lines = client._xml_attributes(name)

    ## THEN make sure that attributes lines are formatted as they should
    assert attribute_lines == ['<Attribute name = "test_name" />']

def test_test_query_biomart_38_xml():
    """Prepare a test xml document for the biomart service build 38 and query the service using it"""
    ## GIVEN a xml file in biomart format
    build = '38'
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE Query>
    <Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" completionStamp = "1">
			
    	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
    		<Filter name = "ensembl_gene_id" value = "ENSG00000115091"/>
    		<Attribute name = "hgnc_symbol" />
    		<Attribute name = "ensembl_transcript_id" />
    	</Dataset>
    </Query>
    """

    ## WHEN querying ensembl
    client = eracs.EnsemblBiomartClient(build='38', xml=xml, header=False)

    ## THEN assert that the result is correct
    i = 0
    for i,line in enumerate(client,1):
        assert 'ACTR3' in line
    assert i > 0

def test_test_query_biomart_37_no_xml():
    """Prepare a test xml document for the biomart service build 37 and query the service using it"""
    ## GIVEN defined biomart filters and attributes
    build = '37'
    filters = { 'ensembl_gene_id' : 'ENSG00000115091' }
    attributes = ['hgnc_symbol', 'ensembl_transcript_id']


    ## WHEN querying ensembl
    client = eracs.EnsemblBiomartClient(build='38', filters=filters, attributes=attributes, header=False)

    i = 0
    for i,line in enumerate(client):
        ## THEN assert the correct gene is fetched
        assert 'ACTR3' in line
    ## THEN assert there was a result
    assert i > 0
