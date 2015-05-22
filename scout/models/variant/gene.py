from __future__ import (absolute_import, unicode_literals, division)

from mongoengine import (EmbeddedDocument, EmbeddedDocumentField, StringField, 
                        ListField, IntField)

from .transcript import Transcript
from . import (SO_TERMS, FEATURE_TYPES, CONSEQUENCE)

from scout.models import PhenotypeTerm

class Gene(EmbeddedDocument):
  hgnc_symbol = StringField(required=True)
  ensembl_gene_id = StringField()
  transcripts = ListField(EmbeddedDocumentField(Transcript))
  functional_annotation = StringField(choices=SO_TERMS)
  region_annotation = StringField(choices=FEATURE_TYPES)
  sift_prediction = StringField(choices=CONSEQUENCE)
  polyphen_prediction = StringField(choices=CONSEQUENCE)
  omim_gene_entry = IntField()
  omim_phenotypes = ListField(EmbeddedDocumentField(PhenotypeTerm))
  description = StringField()

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
