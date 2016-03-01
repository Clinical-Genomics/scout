# -*- coding: utf-8 -*-
from mongoengine import (Document, ListField, StringField, FloatField,
                         IntField, BooleanField)


class Gene(Document):

    meta = {'strict': False}

    chromosome = StringField(required=True)
    start = IntField(required=True)
    stop = IntField(required=True)
    hgnc_symbol = StringField(required=True)
    ensembl_gene_id = StringField(required=True)
    description = StringField()
    locus = StringField()
    mim_id = IntField()
    protein_name = StringField()
    reduced_penetrance = BooleanField(default=False)


class GenePanel(Document):

    meta = {'strict': False}

    institute = StringField(required=True)
    panel_name = StringField(required=True, unique_with='version')
    version = FloatField(required=True)
    date = StringField(required=True)
    display_name = StringField()
    genes = ListField(StringField())

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
