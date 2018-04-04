import logging
import urllib.request
from urllib.error import (HTTPError, URLError)

LOG = logging.getLogger(__name__)

HPO_URL = ("http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/"
           "lastStableBuild/artifact/annotation/{0}")

def fetch_resource(url, file_name=None):
    """Fetch a resource and return the resulting lines in a list
    Send file_name to get more clean log messages
    
    Args:
        url(str)
        file_name(str)
    
    Returns:
        lines(list(str))
    """
    try:
        LOG.info("Requesting %s", (file_name or url))
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
    
    return lines

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
        mim_files[file_name] = fetch_resource(url, file_name)

    return mim_files

def fetch_hpo_terms():
    """Fetch the latest version of the hpo terms in .obo format
    
    Returns:
        res(list(str)): A list with the lines
    """
    url = "http://purl.obolibrary.org/obo/hp.obo"
    
    return fetch_resource(url)
    
def fetch_hpo_to_genes():
    """Fetch the latest version of the map from phenotypes to genes
    
    Returns:
        res(list(str)): A list with the lines
    
    """
    file_name = "ALL_SOURCES_ALL_FREQUENCIES_phenotype_to_genes.txt"
    url = HPO_URL.format(file_name)
    
    return fetch_resource(url, file_name)

def fetch_hpo_genes():
    """Fetch the latest version of the map from genes to hpo terms
    
    Returns:
        res(list(str)): A list with the lines
    
    """
    file_name = "ALL_SOURCES_ALL_FREQUENCIES_genes_to_phenotype.txt"
    url = HPO_URL.format(file_name)
    
    return fetch_resource(url, file_name)

def fetch_hpo_phenotype_to_terms():
    """Fetch the latest version of the map from phenotype to terms
    
    Returns:
        res(list(str)): A list with the lines
    
    """
    file_name = "ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt"
    url = HPO_URL.format(file_name)
    
    return fetch_resource(url, file_name)
