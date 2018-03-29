import logging
import urllib.request
from urllib.error import (HTTPError, URLError)

LOG = logging.getLogger(__name__)

def fetch_mim_files(api_key, mim2genes=False, mimtitles=False, morbidmap=False, genemap2=False):
    """Fetch the necessary mim files using a api key
    
    Args:
        api_key(str): A api key necessary to fetch mim data
    
    Returns:
        mim_files(dict): A dictionary with the neccesary files
    """

    LOG.info("Fetching OMIM files from https://omim.org/")
    mim2genes_url =  'https://omim.org/static/omim/data/mim2gene.txt'
    mimtitles_url= 'https://data.omim.org/downloads/{0}/mimTitles.txt'.format(api_key)
    morbidmap_url = 'https://data.omim.org/downloads/{0}/morbidmap.txt'.format(api_key)
    genemap2_url =  'https://data.omim.org/downloads/{0}/genemap2.txt'.format(api_key)
        
    mim_files = {}
    mim_urls = {}
    
    if mim2genes is True:
        mim_urls['mim2genes'] = mim2genes_url
    if mimtitles is True:
        mim_urls['mimtitles'] = mimtitles_url
    if morbidmap is True:
        mim_urls['morbidmap'] = morbidmap_url
    if genemap2 is True:
        mim_urls['genemap2'] = genemap2_url

    for file_name in mim_urls:
        url = mim_urls[file_name]
        try:
            LOG.info("Requesting %s", file_name)
            response = urllib.request.urlopen(url)
            data = response.read()      # a `bytes` object
            lines = data.decode('utf-8').split('\n')
            mim_files[file_name] = lines
        except HTTPError as err:
            LOG.warning("Something went wrong, perhaps the api key is not valid?")
            raise err
        except URLError as err:
            LOG.warning("Something went wrong, are you connected to internet?")
            raise err

    return mim_files

def fetch_hpo_terms():
    """Fetch the latest version of the hpo terms"""
    url = "http://purl.obolibrary.org/obo/hp.obo"
    
    LOG.info("Requesting %s", url)
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    lines = data.decode('utf-8').split('\n')
    
    return lines

def fetch_hpo_to_genes():
    """Fetch the latest version of the map from genes to hpo terms"""
    url = ("http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/"
           "lastStableBuild/artifact/annotation/ALL_SOURCES_ALL_FREQUENCIE"
           "S_phenotype_to_genes.txt")
    
    LOG.info("Requesting %s", url)
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    lines = data.decode('utf-8').split('\n')
    
    return lines
    