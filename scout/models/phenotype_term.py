# -*- coding: utf-8 -*-
from scout.models import HgncGene

from mongoengine import *

# Hpo terms represents data from the hpo web
hpo_term = dict(
    _id = str, # Same as hpo_id
   hpo_id = str, # Required
   description = str,
   genes = list, # List with integers that are hgnc_ids 
)

# Disease terms represent diseases collected from omim, orphanet and decipher.
# Collected from OMIM
disease_term = dict(
    _id = str, # Same as disease_id
    disease_id = str, # required, like OMIM:600233
    disase_nr = int, # The disease nr
    description = str, # required
    source = str, # required
    genes = list, # List with integers that are hgnc_ids 
)

###############################################################
##################### Old Models ##############################
###############################################################


class HpoTerm(Document):
    hpo_id = StringField(primary_key=True)
    description = StringField()
    genes = ListField(IntField())

    @property
    def hpo_link(self):
        """Return a HPO link."""
        return ("http://compbio.charite.de/hpoweb/showterm?id={}"
                .format(self.hpo_id))

    meta = {
        'index_background': True,
    }

    def __str__(self):
        return ("HpoTerm(hpo_id={this.hpo_id},descriptopn='{this.description}',"
                "genes={this.genes})".format(this=self))

class DiseaseTerm(Document):
    #This is usually the mimnr for the disease
    disease_id = IntField(required=True)

    source = StringField(required=True)

    genes = ListField(IntField())

    meta = {
        'index_background': True,
        'indexes': [
            'genes'
        ]
    }

    @property
    def disease_link(self):
        """Return a disease link to omim or orphanet."""
        link = "http://www.omim.org/entry/{0}"

        if self.source == 'ORPHANET':
            link = "http://www.orpha.net/consor/cgi-bin/Disease_Search.php?"\
                   "lng=EN&data_id={0}"

        elif self.source == 'DECIPHER':
            link = "https://decipher.sanger.ac.uk/syndrome/{0}#overview"

        return link.format(self.disease_id)

    @property
    def display_name(self):
        return ':'.join([self.source, str(self.disease_id)])

    def __str__(self):
        return ("DiseaseTerm(disease_id={this.disease_id},source={this.source},"
                "genes={this.genes})".format(this=self))


class PhenotypeTerm(EmbeddedDocument):
    phenotype_id = StringField()
    feature = StringField()
    disease_models = ListField(StringField())

    @property
    def hpo_link(self):
        """Return a HPO link."""
        return ("http://compbio.charite.de/hpoweb/showterm?id={}"
                .format(self.phenotype_id))

    @property
    def omim_link(self):
        """Return a OMIM phenotype link."""
        return "http://www.omim.org/entry/{}".format(self.phenotype_id)

    def __repr__(self):
        return "PhenotypeTerm(phenotype_id={0}, feature={1}, "\
                "disease_models={2})".format(
                self.phenotype_id, self.feature, self.disease_models
                )
