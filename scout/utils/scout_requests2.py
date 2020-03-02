import logging

import urllib.request
from urllib.error import HTTPError, URLError
from socket import timeout

LOG = logging.getLogger(__name__)

HPO_URL = "http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/util/annotation/{0}"

def get_request(url):
    """Return a requests response from url

    Args:
        url(str)

    Returns:
        decoded_data(str): Decoded response
    """
    try:
        LOG.info("Requesting %s", url)
        response = urllib.request.urlopen(url, timeout=25)
        if url.endswith(".gz"):
            LOG.info("Decompress zipped file")
            data = gzip.decompress(response.read())  # a `bytes` object
        else:
            data = response.read()  # a `bytes` object
        decoded_data = data.decode("utf-8")
    except HTTPError as err:
        LOG.warning("Something went wrong, perhaps the api key is not valid?")
        raise err
    except URLError as err:
        LOG.warning("Something went wrong, are you connected to internet?")
        raise err
    except timeout:
        LOG.error("socket timed out - URL %s", url)
        raise ValueError

    if "Error" in decoded_data:
        raise URLError("Seems like url {} does not exist".format(url))

    return decoded_data


def fetch_hpo_terms():
    """Fetch the latest version of the hpo terms in .obo format

    Returns:
        res(list(str)): A list with the lines
    """
    url = "http://purl.obolibrary.org/obo/hp.obo"

    return fetch_resource(url)


def fetch_hpo_to_genes_to_disease():
    """Fetch the latest version of the map from phenotypes to genes

    Returns:
        res(list(str)): A list with the lines formatted this way:

        #Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol<tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
        HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190
        HP:0000002	Abnormality of body height	197131	UBR1	-	mim2gene	OMIM:243800
        HP:0000002	Abnormality of body height	79633	FAT4		orphadata	ORPHA:314679
    """
    url = HPO_URL.format("phenotype_to_genes.txt")
    return fetch_resource(url)


def fetch_genes_to_hpo_to_disease():
    """Fetch the latest version of the map from genes to phenotypes

    Returns:
        res(list(str)): A list with the lines formatted this way:

        #Format: entrez-gene-id<tab>entrez-gene-symbol<tab>HPO-Term-Name<tab>HPO-Term-ID<tab>Frequency-Raw<tab>Frequency-HPO<tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
        72	ACTG2	HP:0002027	Abdominal pain			-	mim2gene	OMIM:155310
        72	ACTG2	HP:0000368	Low-set, posteriorly rotated ears		HP:0040283		orphadata	ORPHA:2604
    """
    url = HPO_URL.format("genes_to_phenotype.txt")
    return fetch_resource(url)


def fetch_mim_files(
    api_key, mim2genes=False, mimtitles=False, morbidmap=False, genemap2=False
):
    """Fetch the necessary mim files using a api key

    Args:
        api_key(str): A api key necessary to fetch mim data

    Returns:
        mim_files(dict): A dictionary with the neccesary files
    """

    LOG.info("Fetching OMIM files from https://omim.org/")
    mim2genes_url = "https://omim.org/static/omim/data/mim2gene.txt"
    mimtitles_url = "https://data.omim.org/downloads/{0}/mimTitles.txt".format(api_key)
    morbidmap_url = "https://data.omim.org/downloads/{0}/morbidmap.txt".format(api_key)
    genemap2_url = "https://data.omim.org/downloads/{0}/genemap2.txt".format(api_key)

    mim_files = {}
    mim_urls = {}

    if mim2genes is True:
        mim_urls["mim2genes"] = mim2genes_url
    if mimtitles is True:
        mim_urls["mimtitles"] = mimtitles_url
    if morbidmap is True:
        mim_urls["morbidmap"] = morbidmap_url
    if genemap2 is True:
        mim_urls["genemap2"] = genemap2_url

    for file_name in mim_urls:
        url = mim_urls[file_name]
        mim_files[file_name] = fetch_resource(url)

    return mim_files


def fetch_resource(url):
    """Fetch a resource and return the resulting lines in a list
    Send file_name to get more clean log messages

    Args:
        url(str)

    Returns:
        lines(list(str))
    """
    try:
        data = get_request(url)
        lines = data.split("\n")
    except Exception as err:
        raise err

    return lines
