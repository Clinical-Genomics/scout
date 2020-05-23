"""Code for talking to ensembl rest API"""
import logging
from urllib.parse import urlencode

import requests

LOG = logging.getLogger(__name__)

HEADERS = {"Content-type": "application/json"}
RESTAPI_37 = "http://grch37.rest.ensembl.org"
RESTAPI_38 = "http://rest.ensembl.org"
PING_ENDPOINT = "info/ping"

BIOMART_37 = "http://grch37.ensembl.org/biomart/martservice?query="
BIOMART_38 = "http://ensembl.org/biomart/martservice?query="


class EnsemblRestApiClient:
    """A class handling requests and responses to and from the Ensembl REST APIs.
    Endpoints for human build 37: https://grch37.rest.ensembl.org
    Endpoints for human build 38: http://rest.ensembl.org/
    Documentation: https://github.com/Ensembl/ensembl-rest/wiki
    doi:10.1093/bioinformatics/btu613
    """

    def __init__(self, build="37"):
        if build == "38":
            self.server = RESTAPI_38
        else:
            self.server = RESTAPI_37

    def ping_server(self):
        """ping ensembl

        Returns:
            data(dict): dictionary from json response
        """
        url = "/".join([self.server, PING_ENDPOINT])
        data = self.send_request(url)
        return data

    def build_url(self, endpoint, params=None):
        """Build an url to query ensembml"""
        if params:
            endpoint += "?" + urlencode(params)

        return "".join([self.server, endpoint])

    def use_api(self, endpoint, params=None):
        """Sends a request to the Ensembl REST API and returns response data from the service

        Accepts:
            endpoint(str): one of the GET endpoints defined for https://rest.ensembl.org/
            params(dict): dictionary of request parameters

        Returns:
            data(dict): dictionary from json response
        """
        data = None
        if endpoint is None:
            LOG.info("Error: no endpoint specified for Ensembl REST API request.")
            return data

        url = self.build_url(endpoint, params)
        LOG.info("Using Ensembl API with the following url:%s", url)
        data = self.send_request(url)
        return data

    @staticmethod
    def send_request(url):
        """Sends the actual request to the server and returns the response

        Accepts:
            url(str): ex. https://rest.ensembl.org/overlap/id/ENSG00000157764?feature=transcript

        Returns:
            data(dict): dictionary from json response
        """
        data = {}
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 404:
                LOG.info("Request failed for url %s\n", url)
                response.raise_for_status()
            data = response.json()
        except requests.exceptions.MissingSchema as err:
            LOG.info("Request failed for url %s: Error: %s\n", url, err)
            data = err
        except requests.exceptions.HTTPError as err:
            LOG.info("Request failed for url %s: Error: %s\n", url, err)
            data = err
        return data

    def __repr__(self):
        return f"EnsemblRestApiClient:server:{self.server}"


class EnsemblBiomartClient:
    """Class to handle requests to the ensembl biomart api"""

    def __init__(self, build="37", xml=None, filters=None, attributes=None, header=True):
        """Initialise a ensembl biomart client"""
        self.server = BIOMART_37
        if build == "38":
            self.server = BIOMART_38
        self.filters = filters or {}
        self.attributes = attributes or []
        self.xml = xml or self._create_biomart_xml(filters, attributes)
        self.header = header

        LOG.info("Setting up ensembl biomart client with server %s", self.server)

        self.query = self._query_service(xml=self.xml)

        self.attribute_to_header = {
            "chromosome_name": "Chromosome/scaffold name",
            "ensembl_gene_id": "Gene stable ID",
            "ensembl_transcript_id": "Transcript stable ID",
            "ensembl_exon_id": "Exon stable ID",
            "exon_chrom_start": "Exon region start (bp)",
            "exon_chrom_end": "Exon region end (bp)",
            "5_utr_start": "5' UTR start",
            "5_utr_end": "5' UTR end",
            "3_utr_start": "3' UTR start",
            "3_utr_end": "3' UTR end",
            "strand": "Strand",
            "rank": "Exon rank in transcript",
            "transcript_start": "Transcript start (bp)",
            "transcript_end": "Transcript end (bp)",
            "refseq_mrna": "RefSeq mRNA ID",
            "refseq_mrna_predicted": "RefSeq mRNA predicted ID",
            "refseq_ncrna": "RefSeq ncRNA ID",
            "start_position": "Gene start (bp)",
            "end_position": "Gene end (bp)",
            "hgnc_symbol": "HGNC symbol",
            "hgnc_id": "HGNC ID",
        }

    def build_url(self, xml=None):
        """Build a query url"""
        return "".join([self.server, xml])

    def _query_service(self, xml=None, filters=None, attributes=None):
        """Query the Ensembl biomart service and yield the resulting lines

        Accepts:
            xml(str): an xml formatted query, as described here:
                https://grch37.ensembl.org/info/data/biomart/biomart_perl_api.html
            filters(dict): A dictionary with the filters to use and their value
            attributes(list): A list with attributes to use

        Yields:
            biomartline
        """

        url = self.build_url(xml)
        try:
            with requests.get(url, stream=True) as req:
                for line in req.iter_lines():
                    yield line.decode("utf-8")
        except Exception as ex:
            LOG.info("Error downloading data from biomart: %s", ex)
            raise ex

    def _create_biomart_xml(self, filters=None, attributes=None):
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
            "<!DOCTYPE Query>",
            '<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows'
            ' = "0" count = "" datasetConfigVersion = "0.6" completionStamp = "1">',
            "",
            '\t<Dataset name = "hsapiens_gene_ensembl" interface = "default" >',
        ]
        for line in filter_lines:
            xml_lines.append("\t\t" + line)
        for line in attribute_lines:
            xml_lines.append("\t\t" + line)
        xml_lines += ["\t</Dataset>", "</Query>"]

        return "\n".join(xml_lines)

    @staticmethod
    def xml_filters(filters):
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
                formatted_lines.append(
                    '<Filter name = "{0}" value = "{1}"/>'.format(filter_name, value)
                )
            else:
                formatted_lines.append(
                    '<Filter name = "{0}" value = "{1}"/>'.format(filter_name, ",".join(value))
                )

        return formatted_lines

    @staticmethod
    def xml_attributes(attributes):
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

    def _create_header(self, attributes):
        """Create a header line based on the attributes

        Args:
            attributes(list(str))

        Returns:
            header(str)
        """
        headers = []
        for attr in attributes:
            headers.append(self.attribute_to_header[attr])

        return "\t".join(headers)

    def __iter__(self):
        success = False
        if self.header:
            yield self._create_header(self.attributes)

        for line in self.query:
            if line.startswith("["):
                if "success" in line:
                    success = True
                if not success:
                    raise SyntaxError("ensembl request is incomplete")
                LOG.info("successfully retrieved all data from ensembl")
                continue
            yield line
