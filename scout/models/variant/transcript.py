# -*- coding: utf-8 -*-
"""
"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import (absolute_import, unicode_literals, division)

from mongoengine import (EmbeddedDocument, StringField, ListField)

from . import CONSEQUENCE, SO_TERMS, FEATURE_TYPES

class Transcript(EmbeddedDocument):
  transcript_id = StringField(required=True)
  refseq_ids = ListField(StringField())
  hgnc_symbol = StringField()

  # Protein specific predictions
  protein_id = StringField()
  sift_prediction = StringField(choices=CONSEQUENCE)
  polyphen_prediction = StringField(choices=CONSEQUENCE)
  swiss_prot = StringField()
  pfam_domain = StringField()
  prosite_profile = StringField()
  smart_domain = StringField()

  biotype = StringField()
  functional_annotations = ListField(StringField(choices=SO_TERMS))
  region_annotations = ListField(StringField(choices=FEATURE_TYPES))
  exon = StringField()
  intron = StringField()
  strand = StringField()
  coding_sequence_name = StringField()
  protein_sequence_name = StringField()

  @property
  def refseq_ids_string(self):
    return ', '.join(self.refseq_ids)

  @property
  def absolute_exon(self):
    return (self.exon or '').rpartition('/')[0]

  def stringify(self):
    return ("{this.hgnc_symbol}:{this.refseq_ids_string}"
            ":exon{this.absolute_exon}:{this.coding_sequence_name}"
            ":{this.protein_sequence_name}"
            .format(this=self))

  @property
  def swiss_prot_link(self):
    return "http://www.uniprot.org/uniprot/{}".format(self.swiss_prot)

  @property
  def pfam_domain_link(self):
    return "http://pfam.xfam.org/family/{}".format(self.pfam_domain)

  @property
  def prosite_profile_link(self):
    return ("http://prosite.expasy.org/cgi-bin/prosite/prosite-search-ac?{}"
            .format(self.prosite_profile))

  @property
  def smart_domain_link(self):
    return ("http://smart.embl.de/smart/search.cgi?keywords={}"
            .format(self.smart_domain))

  @property
  def refseq_links(self):
    for refseq_id in self.refseq_ids:
      yield (refseq_id,
             "http://www.ncbi.nlm.nih.gov/nuccore/{}".format(refseq_id))

  @property
  def ensembl_link(self):
    return ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?t={}"
            .format(self.transcript_id))