# -*- coding: utf-8 -*-
from mongoengine import (Document, ListField, StringField, FloatField,
                         DateTimeField, BooleanField, EmbeddedDocument,
                         EmbeddedDocumentField, MapField, ReferenceField,
                         IntField, SortedListField)

ACTIONS = ['add', 'delete', 'edit']

class Gene(EmbeddedDocument):

    meta = {'strict': False}

    hgnc_id = IntField(required=True)
    symbol = StringField()

    disease_associated_transcripts = ListField(StringField())
    reduced_penetrance = BooleanField(default=False)
    mosaicism = BooleanField(default=False)
    database_entry_version = StringField()
    inheritance_models = ListField(StringField())
    curator = StringField()

    ar = BooleanField()
    ad = BooleanField()
    mt = BooleanField()
    xr = BooleanField()
    xd = BooleanField()
    x = BooleanField()
    y = BooleanField()

    action = StringField(choices=ACTIONS)

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
    pending_genes = ListField(EmbeddedDocumentField(Gene)) # Used when updating gene panels

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
        date_obj = self.date.date()
        return ("{this.display_name} ({this.version}, {date})"
                .format(this=self, date=date_obj))

    def __unicode__(self):
        return self.name_and_version()

    def __str__(self):
        return self.name_and_version()

    def __repr__(self):
        return ("GeneList(name={0}, version={1}, date={2}, display_name={3})"
                .format(self.panel_name, self.version, self.date,
                        self.display_name))
