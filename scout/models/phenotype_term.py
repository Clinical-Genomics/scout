# -*- coding: utf-8 -*-
from mongoengine import (Document, EmbeddedDocument, StringField, ListField,
                         ReferenceField, IntField)

from scout.models import HgncGene

class HpoTerm(Document):
    hpo_id = StringField(required=True, unique=True)
    description = StringField()
    genes = ListField(ReferenceField('HgncGene'))

    @property
    def hpo_link(self):
        """Return a HPO link."""
        return ("http://compbio.charite.de/hpoweb/showterm?id={}"
                .format(self.hpo_id))

    meta = {
        'index_background': True,
        'indexes':[
            'hpo_id',
        ]
    }

class DiseaseTerm(Document):
    #This is usually the mimnr for the disease
    disease_id = IntField(required=True, unique=True)
    
    genes = ListField(ReferenceField('HgncGene'))
    hpo_terms = ListField(ReferenceField('HpoTerm'))
    
    @property
    def omim_link(self):
        """Return a OMIM phenotype link."""
        return "http://www.omim.org/entry/{}".format(self.disease_id)

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

