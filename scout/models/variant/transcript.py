# -*- coding: utf-8 -*-
"""
"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import (absolute_import, division)

from mongoengine import (EmbeddedDocument, StringField, ListField, BooleanField,
                         IntField)

from scout.constants import (SO_TERM_KEYS, CONSEQUENCE, FEATURE_TYPES)


class Transcript(EmbeddedDocument):
    # The ensemble transcript id
    transcript_id = StringField(required=True)
    # The hgnc gene id
    hgnc_id = IntField()

    ### Protein specific predictions ###
    # The ensemble protein id
    protein_id = StringField()
    # The sift consequence prediction for this transcript
    sift_prediction = StringField(choices=CONSEQUENCE)
    # The polyphen consequence prediction for this transcript
    polyphen_prediction = StringField(choices=CONSEQUENCE)
    # The swiss protein id for the product
    swiss_prot = StringField()
    # The pfam id for the protein product
    pfam_domain = StringField()
    # The prosite id for the product
    prosite_profile = StringField()
    # The smart id for the product
    smart_domain = StringField()

    # The biotype annotation for the transcript
    biotype = StringField()
    # The functional annotations for the transcript
    functional_annotations = ListField(StringField(choices=SO_TERM_KEYS))
    # The region annotations for the transcripts
    region_annotations = ListField(StringField(choices=FEATURE_TYPES))
    # The exon number in the transcript e.g '2/7'
    exon = StringField()
    # The intron number in the transcript e.g '4/6'
    intron = StringField()
    # The strand of the transcript e.g '+'
    strand = StringField()
    # the CDNA change of the transcript e.g 'c.95T>C'
    coding_sequence_name = StringField()
    # The amino acid change on the transcript e.g. 'p.Phe32Ser'
    protein_sequence_name = StringField()

    # If the transcript is relevant
    is_canonical = BooleanField()

    @property
    def absolute_exon(self):
        return (self.exon or '').rpartition('/')[0]

    def is_exonic(self):
        """Determine if transcript is exonic or not."""
        return 'exonic' in self.region_annotations

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
    def ensembl_link(self):
        return ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?t={}"
                .format(self.transcript_id))
