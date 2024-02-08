"""Code for performing requests"""
import logging
import urllib.request
import zlib
from typing import Dict
from urllib.error import HTTPError

import requests
from defusedxml import ElementTree
from flask import flash

from scout.constants import HPO_URL, HPOTERMS_URL, ORPHA_URLS

LOG = logging.getLogger(__name__)
TIMEOUT = 20


def post_request_json(url, data, headers=None, cookies=None):
    """Send json data via POST request and return response

    Args:
        url(str): url to send request to
        data(dict): data to be sent
        headers(dict): request headers
        cookies(dict): cookies to pass with request

    Returns:
        json_response(dict)
    """
    json_response = {}
    try:
        LOG.debug(f"Sending POST request with json data to {url}")
        resp = requests.post(url, headers=headers, cookies=cookies, json=data)
        json_response["content"] = resp.json()

    except Exception as ex:
        return {"message": f"An error occurred while sending a POST request to url {url} -> {ex}"}

    json_response["status_code"] = resp.status_code
    return json_response


def get_request_json(url, headers=None, cookies=None):
    """Send GET request and return response's json data
    Args:
        url(str): url to send request to
        headers(dict): eventual request HEADERS to use in request
        cookies(dict): cookies to pass with request
    Returns:
        json_response(dict), example {"status_code":200, "content":{original json content}}
    """
    json_response = {}
    try:
        LOG.debug(f"Sending GET request to {url}")
        resp = requests.get(url, timeout=TIMEOUT, headers=headers, cookies=cookies)
        json_response["content"] = resp.json()

    except Exception as ex:
        return {"message": f"An error occurred while sending a GET request to url {url} -> {ex}"}

    json_response["status_code"] = resp.status_code
    return json_response


def delete_request_json(url, headers=None, data=None):
    """Send a DELETE request to a remote API and return its response
    Args:
        url(str): url to send request to
        headers(dict): eventual request HEADERS to use in request
        data(dict): eventual request data to ba passed as a json object
    Returns:
        json_response(dict)
    """
    json_response = {}
    try:
        LOG.debug(f"Sending DELETE request to {url}")
        if headers and data:
            resp = requests.delete(url, headers=headers, json=data)
        elif headers:
            resp = requests.delete(url, headers=headers)
        else:
            resp = requests.delete(url)
        json_response["content"] = resp.json()

    except Exception as ex:
        return {"message": f"An error occurred while sending a DELETE request to url {url} -> {ex}"}

    json_response["status_code"] = resp.status_code
    return json_response


def get_request(url):
    """Return a requests response from url

    Args:
        url(str)

    Returns:
        decoded_data(str): Decoded response
    """
    response = None
    error = None
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code != 200:
            response.raise_for_status()
    except requests.exceptions.HTTPError:
        error = "Something went wrong, perhaps the api key is not valid?"
    except requests.exceptions.MissingSchema:
        error = "Something went wrong, perhaps url is invalid?"
    except requests.exceptions.Timeout:
        error = f"socket timed out - URL {url}"
    except Exception as ex:
        error = f"Exception while connecting to {url}: {ex}"

    if error:
        LOG.error(error)
        return

    return response


def fetch_resource(url, json=False):
    """Fetch a resource and return the resulting lines in a list or a json object
    Send file_name to get more clean log messages

    Args:
        url(str)
        json(bool): if result should be in json

    Returns:
        data
    """
    if url.startswith("ftp"):
        # requests do not handle ftp
        response = urllib.request.urlopen(url, timeout=TIMEOUT)
        if isinstance(response, Exception):
            raise response
        data = response.read().decode("utf-8")
        return data.split("\n")

    response = get_request(url)

    if json:
        LOG.info("Return in json")
        data = response.json()
    else:
        content = response.text
        if response.url.endswith(".gz"):
            LOG.info("gzipped!")
            encoded_content = b"".join(chunk for chunk in response.iter_content(chunk_size=128))
            content = zlib.decompress(encoded_content, 16 + zlib.MAX_WBITS).decode("utf-8")

        data = content.split("\n")

    return data


def fetch_hpo_terms():
    """Fetch the latest version of the hpo terms in .obo format

    Returns:
        res(list(str)): A list with the lines
    """
    url = HPOTERMS_URL

    return fetch_resource(url)


def fetch_genes_to_hpo_to_disease():
    """Fetch the latest version of the map from genes to phenotypes
        Returns:
        res(list(str)): A list with the lines formatted this way:
        #Format: entrez-gene-id<tab>entrez-gene-symbol<tab>HPO-Term-Name<tab>\
        HPO-Term-ID<tab>Frequency-Raw<tab>Frequency-HPO<tab>
        Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
        72	ACTG2	HP:0002027	Abdominal pain			-	mim2gene	OMIM:155310
        72	ACTG2	HP:0000368	Low-set, posteriorly rotated ears		HP:0040283		orphadata
        ORPHA:2604
    """
    url = HPO_URL.format("genes_to_phenotype.txt")
    return fetch_resource(url)


def fetch_hpo_to_genes_to_disease():
    """Fetch the latest version of the map from phenotypes to genes

    Returns:
        res(list(str)): A list with the lines formatted this way:

        #Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol\
        <tab>Additional Info from G-D source<tab>G-D source
        <tab>disease-ID for link
        HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190
        HP:0000002	Abnormality of body height	197131	UBR1	-	mim2gene	OMIM:243800
        HP:0000002	Abnormality of body height	79633	FAT4		orphadata	ORPHA:314679

    """
    url = HPO_URL.format("phenotype_to_genes.txt")
    return fetch_resource(url)


def fetch_hpo_disease_annotation():
    """Fetch the latest version of the map from phenotypes to genes

    Returns:
        res(list(str)): A list with the lines formatted this way:

        #description: "HPO annotations for rare diseases [8120: OMIM; 47: DECIPHER; 4264 ORPHANET]"
        #version: 2023-04-05
        #tracker: https://github.com/obophenotype/human-phenotype-ontology/issues
        #hpo-version: http://purl.obolibrary.org/obo/hp/releases/2023-04-05/hp.json
        database_id     disease_name    qualifier       hpo_id  reference       evidence        onset   frequency       sex     modifier        aspect  biocuration
        OMIM:619340     Developmental and epileptic encephalopathy 96           HP:0011097      PMID:31675180   PCS             1/2                     P       HPO:probinson[2021-06-21]
        OMIM:619340     Developmental and epileptic encephalopathy 96           HP:0002187      PMID:31675180   PCS             1/1                     P       HPO:probinson[2021-06-21]
        ...
        OMIM:609153     Pseudohyperkalemia, familial, 2, due to red cell leak           HP:0002378      PMID:2766660    PCS                                     P       HPO:lccarmody[2018-10-03]
        OMIM:609153     Pseudohyperkalemia, familial, 2, due to red cell leak           HP:0003324      PMID:2766660    PCS                                     P       HPO:lccarmody[2018-10-03]
        OMIM:609153     Pseudohyperkalemia, familial, 2, due to red cell leak           HP:0002153      PMID:2766660    PCS                                     P       HPO:lccarmody[2018-10-03];HPO:lccarmody[2018-10-03]
        ...
    """
    url = HPO_URL.format("phenotype.hpoa")
    return fetch_resource(url)


def fetch_hpo_files(
    genes_to_phenotype=False,
    phenotype_to_genes=False,
    hpo_terms=False,
    hpo_annotation=False,
):
    """
    Fetch the necessary HPO files from http://compbio.charite.de

    Args:
        genes_to_phenotype(bool): if file genes_to_phenotype.txt is required
        phenotype_to_genes(bool): if file phenotype_to_genes.txt is required
        hpo_terms(bool):if file hp.obo is required

    Returns:
        hpo_files(dict): A dictionary with the necessary files
    """
    LOG.info("Fetching HPO information from http://compbio.charite.de")

    hpo_files = {}

    if genes_to_phenotype is True:
        hpo_files["genes_to_phenotype"] = fetch_genes_to_hpo_to_disease()
    if phenotype_to_genes is True:
        hpo_files["phenotype_to_genes"] = fetch_hpo_to_genes_to_disease()
    if hpo_terms is True:
        hpo_files["hpo_terms"] = fetch_hpo_terms()
    if hpo_annotation is True:
        hpo_files["hpo_annotation"] = fetch_hpo_disease_annotation()

    return hpo_files


def fetch_mim_files(api_key, mim2genes=False, mimtitles=False, morbidmap=False, genemap2=False):
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


def fetch_orpha_files() -> Dict:
    """Fetch the requested files from orphadata
    https://www.orphadata.com/data/xml/en_product{nr}.xml
    """
    LOG.info("Fetching orpha files from orphadata")

    orpha_files = {}

    orpha_files["orphadata_en_product4"] = fetch_resource(ORPHA_URLS["orpha_to_hpo"])
    orpha_files["orphadata_en_product6"] = fetch_resource(ORPHA_URLS["orpha_to_genes"])
    orpha_files["en_product9_ages"] = fetch_resource(ORPHA_URLS["orpha_inheritance"])

    return orpha_files


def fetch_hgnc():
    """Fetch the hgnc genes file from
        ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt

    Returns:
        hgnc_gene_lines(list(str))
    """
    file_name = "hgnc_complete_set.txt"
    url = "ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/{0}".format(file_name)
    LOG.info("Fetching HGNC genes from %s", url)

    hgnc_lines = fetch_resource(url)

    return hgnc_lines


def fetch_constraint():
    """Fetch the file with gnomAD constraint scores

    Returns:
        exac_lines(iterable(str))
    """
    path = "/release/v4.0/constraint/gnomad.v4.0.constraint_metrics.tsv"
    mirror_urls = [
        f"https://storage.googleapis.com/gcp-public-data--gnomad{path}",
        f"https://gnomad-public-us-east-1.s3.amazonaws.com{path}",
        f"https://datasetgnomad.blob.core.windows.net/dataset{path}",
    ]

    exac_lines = None

    LOG.info("Fetching GnomAD constraint scores.")

    for url in mirror_urls:
        try:
            exac_lines = fetch_resource(url)
        except HTTPError:
            LOG.info("Failed to fetch constraint scores from %s. Trying next mirror.", url)

        return exac_lines


def fetch_refseq_version(refseq_acc):
    """Fetch refseq version from entrez and return refseq version

    Args:
        refseq_acc(str) example: NM_020533

    Returns
        version(str) example: NM_020533.3 or NM_020533 if no version associated is found
    """
    version = refseq_acc
    base_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&"
        "term={}&idtype=acc"
    )

    try:
        resp = get_request(base_url.format(refseq_acc))
        if resp is None:
            flash(f"Error: could not retrieve HGVS version for {refseq_acc} from Entrez eutils!")
            return version
        tree = ElementTree.fromstring(resp.content)
        version = tree.find("IdList").find("Id").text or version

    except (
        requests.exceptions.HTTPError,
        requests.exceptions.MissingSchema,
        AttributeError,
    ):
        LOG.warning("refseq accession not found")

    return version
