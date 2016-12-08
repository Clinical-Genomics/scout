# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import
from datetime import datetime

from mongoengine import (DateTimeField, Document, EmailField, IntField,
                         ListField, StringField, FloatField)


class Institute(Document):

    """Represents an institute linked to multiple collaborating users."""

    meta = {'strict': False}

    internal_id = StringField(primary_key=True, required=True)
    display_name = StringField(required=True)
    sanger_recipients = ListField(EmailField())
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    coverage_cutoff = IntField(default=10)
    frequency_cutoff = FloatField(default=0.01)

    def cases(self, Case):
        """Return all cases that have the institute as owner."""
        return Case.objects(owner=self.internal_id)

    def __unicode__(self):
        return self.display_name

    def __repr__(self):
        return ("Institute(internal_id={this.internal_id}, "
                "display_name={this.display_name}, "
                "sanger_recipients={this.sanger_recipients}, "
                "created_at={this.created_at})".format(this=self))
