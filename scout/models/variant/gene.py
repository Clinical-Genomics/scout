from __future__ import (absolute_import, division)

from mongoengine import (EmbeddedDocument, EmbeddedDocumentField, StringField, 
                        ListField, IntField, BooleanField)

from .transcript import Transcript
from . import (SO_TERMS, FEATURE_TYPES, CONSEQUENCE)

from scout.models import PhenotypeTerm

class Gene(EmbeddedDocument):
  # The hgnc gene symbol
  hgnc_symbol = StringField(required=True)
  # The ensembl gene id
  ensembl_gene_id = StringField()
  # A list of Transcript objects
  transcripts = ListField(EmbeddedDocumentField(Transcript))
  # This is the worst functional impact of all transcripts
  functional_annotation = StringField(choices=SO_TERMS)
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
