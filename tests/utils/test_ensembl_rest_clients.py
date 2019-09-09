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
    xml_lines = client.xml_filters(filters)

    # make sure lines are formatted as they should
    assert '<Filter name = "{0}" value = "{1}"/>'.format('string_filter', 'string_value') in xml_lines
    assert '<Filter name = "{0}" value = "{1}"/>'.format('list_filter', '1,X,MT') in xml_lines

def test_xml_attributes():
    """test method that creates attribute lines for the biomart xml file"""

    # Having a list of  biomart attributes
    name = ["test_name"]
    client = eracs.EnsemblBiomartClient()
    attribute_lines = client.xml_attributes(name)

    # Make sure that attributes lines are formatted as they should
    assert attribute_lines == ['<Attribute name = "test_name" />']

def test_test_query_biomart_38_xml():
    """Prepare a test xml document for the biomart service build 38 and query the service using it"""
    client = eracs.EnsemblBiomartClient(build='38')

    # having defined biomart filters and attributes
    filters = { 'ensembl_gene_id' : 'ENSG00000115091' }
    attributes = ['hgnc_symbol', 'ensembl_transcript_id']

    # use client method to create a formatted xml query file
    formatted_xml = client.create_biomart_xml(filters, attributes)

    # and download data to file
    res = client.query_service(formatted_xml)

    i = 0
    for i,line in enumerate(res,1):
        print(line)
        if line.startswith('['):
            continue
        assert 'ACTR3' in line
    assert i > 0

def test_test_query_biomart_37_no_xml():
    """Prepare a test xml document for the biomart service build 37 and query the service using it"""
    client = eracs.EnsemblBiomartClient(build='37')

    ## GIVEN defined biomart filters and attributes
    filters = { 'ensembl_gene_id' : 'ENSG00000115091' }
    attributes = ['hgnc_symbol', 'ensembl_transcript_id']

    ## WHEN fetching data from ensembl biomart
    res = client.query_service(filters=filters, attributes=attributes)

    i = 0
    for i,line in enumerate(res):
        if line.startswith('['):
            continue
        ## THEN assert the correct gene is fetched
        assert 'ACTR3' in line
    ## THEN assert there was a result
    assert i > 0
        
