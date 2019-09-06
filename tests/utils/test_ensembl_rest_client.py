# -*- coding: UTF-8 -*-
import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from scout.utils import ensembl_rest_client

XML_EXON_QUERY = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

	<Dataset name = "hsapiens_gene_ensembl" interface = "default" >
		<Filter name = "chromosome_name" value = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,MT,X,Y"/>
		<Attribute name = "ensembl_gene_id" />
		<Attribute name = "ensembl_transcript_id" />
		<Attribute name = "strand" />
		<Attribute name = "5_utr_start" />
		<Attribute name = "5_utr_end" />
		<Attribute name = "3_utr_start" />
		<Attribute name = "3_utr_end" />
		<Attribute name = "exon_chrom_start" />
		<Attribute name = "exon_chrom_end" />
		<Attribute name = "rank" />
		<Attribute name = "ensembl_exon_id" />
	</Dataset>
</Query>"""

def test_ping_ensemble_37():
    """Test ping ensembl server containing human build 37"""
    client = ensembl_rest_client.EnsemblRestClient()
    data = client.ping_server()
    assert data == {'ping':1}

def test_ping_ensemble_38():
    """Test ping ensembl server containing human build 38"""
    client = ensembl_rest_client.EnsemblRestClient(build='38')
    data = client.ping_server()
    assert data == {'ping':1}

def test_send_gene_request():
    """Test send request with correct params and endpoint"""
    url = 'https://grch37.rest.ensembl.org/overlap/id/ENSG00000103591?feature=gene'
    client = ensembl_rest_client.EnsemblRestClient()
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
    client = ensembl_rest_client.EnsemblRestClient()
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
    client = ensembl_rest_client.EnsemblRestClient(build='38')

    # get all transctipts for an ensembl gene, They should be a list of items
    data = client.use_api(endpoint, params)
    assert data[0]['assembly_name'] == 'GRCh38'
    assert data[0]['feature_type'] == 'transcript'
    assert data[0]['id']
    assert data[0]['start']
    assert data[0]['strand']

def test_create_xml_filter():
    """test method that creates filter lines for the biomart xml file"""

    name = 'test_name'
    string_value = 'string_value'

    client = ensembl_rest_client.EnsemblRestClient()
    line = client.xml_filter(name, string_value)

    # make sure line is formatted as it should
    assert line == '<Filter name = "{0}" value = "{1}"/>'.format(name, string_value)

    # test with a value of type == list
    list_value = [1,'X','MT']
    line = client.xml_filter(name, list_value)
    assert line == '<Filter name = "{0}" value = "{1}"/>'.format(name, ','.join(str(list_value)))


def test_create_xml_attribute():
    """test method that creates attribute lines for the biomart xml file"""

    name = "test_name"
    client = ensembl_rest_client.EnsemblRestClient()
    line = client.xml_attribute(name)

    # Make sure that attribute line is formatted as it should
    assert line == '<Attribute name = "{}" />'.format(name)

def test_create_biomart_xml():
    """Prepare a test xml document for the biomart service"""

    client = ensembl_rest_client.EnsemblRestClient()
    filters= [ ('chromosome_name' , [1,2,'X']) ]
    attributes = ['ensembl_gene_id', 'ensembl_transcript_id']
    client = ensembl_rest_client.EnsemblRestClient()

    # use client methof to create a formatted xml query file
    formatted_xml = client.create_biomart_xml(filters, attributes)
    assert formatted_xml































#def test_use_api():
#    """Test the API by retrieving all the available info for a gene,
#       including transcripts and exons.
#    """
    # default client will be querying agast build 37
#    client = ensembl_rest_client.EnsemblRestClient()
#    regions = [1:]














#def test_perform_rest_action():
#    """Tests the perform_rest_action method of the EnsemblRestClient"""

#    client = ensembl_rest_client.EnsemblRestClient()
