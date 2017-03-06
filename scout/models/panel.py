# -*- coding: utf-8 -*-
from datetime import datetime

from mongoengine import (Document, ListField, StringField, FloatField,
                         DateTimeField, BooleanField, EmbeddedDocument,
                         EmbeddedDocumentField, MapField, ReferenceField,
                         IntField, SortedListField)


panel_gene = dict(
    hgnc_id = int, # required
    symbol = str, 

    disease_associated_transcripts = list, # list of strings that represent refseq transcripts
    reduced_penetrance = bool, 
    mosaicism = bool, 
    database_entry_version = str,

    ar = bool,
    ad = bool,
    mt = bool,
    xr = bool,
    xd = bool,
    x = bool,
    y = bool,

)


## gene panel should be indexed on genes.hgnc_id
gene_panel = dict(
    panel_name = str, # required
    institute = str, # institute_id
    version = float, # required
    date = datetime, # required
    display_name = str, # default is panel_name
    genes = list, # list of panel genes, sorted on panel_gene['symbol']
)

class Gene(EmbeddedDocument):

    meta = {'strict': False}

    hgnc_id = IntField(required=True)
    symbol = StringField()

    disease_associated_transcripts = ListField(StringField())
    reduced_penetrance = BooleanField(default=False)
    mosaicism = BooleanField(default=False)
    database_entry_version = StringField()

    ar = BooleanField()
    ad = BooleanField()
    mt = BooleanField()
    xr = BooleanField()
    xd = BooleanField()
    x = BooleanField()
    y = BooleanField()

    def __unicode__(self):
        return "{this.hgnc_id}: {this.symbol}".format(this=self)


class GenePanel(Document):

    meta = {
        'strict': False,
        'index_background': True,
        'indexes': ['genes.hgnc_id']
    }

    panel_name = StringField(required=True, unique_with='version')
    institute = StringField()
    version = FloatField(required=True)
    date = DateTimeField(required=True)
    display_name = StringField()
    # {'ADK':Gene}
    genes = SortedListField(EmbeddedDocumentField(Gene), ordering='symbol')

    @property
    def gene_ids(self):
        for gene in self.genes:
            yield gene.hgnc_id

    @property
    def gene_symbols(self):
        for gene in self.genes:
            yield gene.symbol

    @property
    def name_and_version(self):
        """Return the name of the panel and version."""
        return "{this.display_name} ({this.version})".format(this=self)

    def __unicode__(self):
        return "{this.panel_name} ({this.version})".format(this=self)

    def __repr__(self):
        return ("GeneList(name={0}, version={1}, date={2}, display_name={3})"
                .format(self.panel_name, self.version, self.date,
                        self.display_name))
