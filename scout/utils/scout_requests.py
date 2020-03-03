import xml.etree.ElementTree as et
import logging
import gzip
import urllib.request
from urllib.error import HTTPError, URLError
from socket import timeout

from scout.constants import CHROMOSOMES
from scout.utils.ensembl_rest_clients import EnsemblBiomartClient

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
        response = urllib.request.urlopen(url, timeout=20)
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


def fetch_hpo_terms():
    """Fetch the latest version of the hpo terms in .obo format

    Returns:
        res(list(str)): A list with the lines
    """
    url = "http://purl.obolibrary.org/obo/hp.obo"

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


def fetch_ensembl_biomart(attributes, filters, build=None):
    """Fetch data from ensembl biomart

    Args:
        attributes(list): List of selected attributes
        filters(dict): Select what filters to use
        build(str): '37' or '38'

    Returns:
        client(EnsemblBiomartClient)
    """
    build = build or "37"

    client = EnsemblBiomartClient(build=build, filters=filters, attributes=attributes)
    LOG.info("Selecting attributes: {0}".format(", ".join(attributes)))
    LOG.info("Use filter: {0}".format(filters))

    return client


def fetch_ensembl_genes(build=None):
    """Fetch the ensembl genes

    Args:
        build(str): ['37', '38']

    Returns:
        result(iterable): Ensembl formated gene lines
    """
    LOG.info("Fetching ensembl genes")

    attributes = [
        "chromosome_name",
        "start_position",
        "end_position",
        "ensembl_gene_id",
        "hgnc_symbol",
        "hgnc_id",
    ]

    filters = {"chromosome_name": CHROMOSOMES}

    return fetch_ensembl_biomart(attributes, filters, build)


def fetch_ensembl_transcripts(build=None, chromosomes=None):
    """Fetch the ensembl genes

    Args:
        build(str): ['37', '38']
        chromosomes(iterable(str))

    Returns:
        result(iterable): Ensembl formated transcript lines
    """
    chromosomes = chromosomes or CHROMOSOMES
    LOG.info("Fetching ensembl transcripts")

    attributes = [
        "chromosome_name",
        "ensembl_gene_id",
        "ensembl_transcript_id",
        "transcript_start",
        "transcript_end",
        "refseq_mrna",
        "refseq_mrna_predicted",
        "refseq_ncrna",
    ]

    filters = {"chromosome_name": chromosomes}

    return fetch_ensembl_biomart(attributes, filters, build)


def fetch_ensembl_exons(build=None, chromosomes=None):
    """Fetch the ensembl genes

    Args:
        build(str): ['37', '38']
        chromosomes(iterable(str))
    """
    chromosomes = chromosomes or CHROMOSOMES
    LOG.info("Fetching ensembl exons")

    attributes = [
        "chromosome_name",
        "ensembl_gene_id",
        "ensembl_transcript_id",
        "ensembl_exon_id",
        "exon_chrom_start",
        "exon_chrom_end",
        "5_utr_start",
        "5_utr_end",
        "3_utr_start",
        "3_utr_end",
        "strand",
        "rank",
    ]

    filters = {"chromosome_name": chromosomes}

    return fetch_ensembl_biomart(attributes, filters, build)


def fetch_hgnc():
    """Fetch the hgnc genes file from
        ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt

    Returns:
        hgnc_gene_lines(list(str))
    """
    file_name = "hgnc_complete_set.txt"
    url = "ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/{0}".format(file_name)
    LOG.info("Fetching HGNC genes")

    hgnc_lines = fetch_resource(url)

    return hgnc_lines


def fetch_exac_constraint():
    """Fetch the file with exac constraint scores

    Returns:
        exac_lines(iterable(str))
    """
    file_name = "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt"
    url = (
        "ftp://ftp.broadinstitute.org/pub/ExAC_release/release0.3/functional_gene_constraint"
        "/{0}"
    ).format(file_name)

    exac_lines = None

    LOG.info("Fetching ExAC genes")

    try:
        exac_lines = fetch_resource(url)
    except URLError as err:
        LOG.info("Failed to fetch exac constraint scores file from ftp server")
        LOG.info("Try to fetch from google bucket...")
        url = (
            "https://storage.googleapis.com/gnomad-public/legacy/exacv1_downloads/release0.3.1"
            "/manuscript_data/forweb_cleaned_exac_r03_march16_z_data_pLI.txt.gz"
        )

    if not exac_lines:
        exac_lines = fetch_resource(url)

    return exac_lines


def fetch_hpo_files(genes_to_phenotype=False, phenotype_to_genes=False):
    """
    Fetch the necessary HPO files from http://compbio.charite.de

    Args:
        genes_to_phenotype(bool): if file genes_to_phenotype.txt is required
        phenotype_to_genes(bool): if file phenotype_to_genes.txt is required

    Returns:
        hpo_files(dict): A dictionary with the necessary files
    """
    LOG.info("Fetching HPO information from http://compbio.charite.de")

    hpo_files = {}
    hpo_urls = {}

    if genes_to_phenotype is True:
        hpo_urls["genes_to_phenotype"] = base_url.format("genes_to_phenotype.txt")
    if phenotype_to_genes is True:
        hpo_urls["phenotype_to_genes"] = base_url.format("phenotype_to_genes.txt")

    for file_name in hpo_urls:
        url = hpo_urls[file_name]
        hpo_files[file_name] = request_file(url)

    return hpo_files


def fetch_refseq_version(refseq_acc):
    """Fetch refseq version from entrez and return refseq version

    Args:
        refseq_acc(str) example: NM_020533

    Returns
        version(str) example: NM_020533.3 or NM_020533 if no version associated is found
    """
    version = refseq_acc
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term={}&idtype=acc".format(
        refseq_acc
    )

    try:
        resp = urllib.request.urlopen(base_url)
        xml_response = et.parse(resp)
        version = xml_response.find("IdList").find("Id").text or version

    except HTTPError as err:
        LOG.warning("Something went wrong, perhaps the refseq accession is not valid?")
    except URLError as err:
        LOG.warning("Something went wrong, are you connected to internet?")
    except AttributeError as err:
        LOG.warning("refseq accession not found")

    return version
