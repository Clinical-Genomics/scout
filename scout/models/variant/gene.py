from __future__ import absolute_import, division
from mongoengine import (EmbeddedDocument, EmbeddedDocumentField, StringField,
                         ListField, IntField, BooleanField)

from .transcript import Transcript
from scout.constants import (CONSEQUENCE, FEATURE_TYPES, SO_TERMS)

from scout.models import PhenotypeTerm


class Gene(EmbeddedDocument):
    # The hgnc gene symbol
    hgnc_symbol = StringField(required=True)
    # The ensembl gene id
    ensembl_gene_id = StringField()
    # A list of Transcript objects
    transcripts = ListField(EmbeddedDocumentField(Transcript))
    # This is the worst functional impact of all transcripts
    functional_annotation = StringField(choices=SO_TERMS.keys())
    # This is the region of the most severe functional impact
    region_annotation = StringField(choices=FEATURE_TYPES)
    # This is most severe sift prediction of all transcripts
    sift_prediction = StringField(choices=CONSEQUENCE)
    # This is most severe polyphen prediction of all transcripts
    polyphen_prediction = StringField(choices=CONSEQUENCE)
    omim_gene_entry = IntField()
    omim_phenotypes = ListField(EmbeddedDocumentField(PhenotypeTerm))
    description = StringField()
    reduced_penetrance = BooleanField()

    disease_associated_transcripts = ListField(StringField())

    @property
    def reactome_link(self):
        url_template = ("http://www.reactome.org/content/query?q={}&"
                        "species=Homo+sapiens&species=Entries+without+species&"
                        "cluster=true")
        return url_template.format(self.ensembl_gene_id)

    @property
    def ensembl_link(self):
        return ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?g={}"
                .format(self.ensembl_gene_id))

    @property
    def hpa_link(self):
        return ("http://www.proteinatlas.org/search/{}"
                .format(self.ensembl_gene_id))

    @property
    def string_link(self):
        return ("http://string-db.org/newstring_cgi/show_network_section."
                "pl?identifier={}".format(self.ensembl_gene_id))

    @property
    def entrez_link(self):
        return ("http://www.ncbi.nlm.nih.gov/sites/gquery/?term={}"
                .format(self.hgnc_symbol))

    @property
    def expression_atlas_link(self):
        url_template = ("https://www.ebi.ac.uk/gxa/genes/{}?"
                        "bs=%7B%22homo+sapiens%22%3A%7B%22CELL_LINE%22%3Atrue"
                        "%2C%22ORGANISM_PART%22%3Atrue%7D%7D&ds=%7B%22species"
                        "%22%3A%7B%22homo+sapiens%22%3Atrue%7D%7D")
        return url_template.format(self.ensembl_gene_id)

    @property
    def omim_link(self):
        return "http://omim.org/entry/{}".format(self.omim_gene_entry)
