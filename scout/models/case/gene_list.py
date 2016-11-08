# -*- coding: utf-8 -*-
from mongoengine import (Document, ListField, StringField, FloatField,
                         IntField, BooleanField, EmbeddedDocument, 
                         EmbeddedDocumentField, MapField)

class Gene(EmbeddedDocument):

    meta = {'strict': False}

    hgnc_symbol = StringField(required=True)

    disease_associated_transcripts = ListField(StringField())
    reduced_penetrance = BooleanField(default=False)


class GenePanel(Document):

    meta = {'strict': False}

    panel_name = StringField(required=True, unique_with='version')
    version = FloatField(required=True)
    date = StringField(required=True)
    display_name = StringField()
    # This is a list of hgnc symbols
    genes = ListField(StringField())
    # This is a list of gene objects
    gene_objects = MapField(EmbeddedDocumentField(Gene))

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
