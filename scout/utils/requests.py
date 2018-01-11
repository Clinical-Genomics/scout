import logging
import urllib.request
from urllib.error import (HTTPError, URLError)

LOG = logging.getLogger(__name__)

def fetch_mim_files(api_key):
    """Fetch the necessary mim files using a api key
    
    Args:
        api_key(str): A api key necessary to fetch mim data
    
    Returns:
        mim_files(dict): A dictionary with the neccesary files
    """
    LOG.info("Fetching OMIM files from https://omim.org/")
    
    mim_files = {}
    mim_urls = { 
        'mim2genes': 'https://omim.org/static/omim/data/mim2gene.txt',
        'mimtitles': 'https://data.omim.org/downloads/{0}/mimTitles.txt'.format(api_key),
        'morbidmap': 'https://data.omim.org/downloads/{0}/morbidmap.txt'.format(api_key),
        'genemap2': 'https://data.omim.org/downloads/{0}/genemap2.txt'.format(api_key)
    }

    
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