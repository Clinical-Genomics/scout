from __future__ import unicode_literals

from mongoengine import (Document, StringField, ListField)

class HgncAlias(Document):
    #This works like a dictionary where hgnc_symbol is the correct id and
    #values are all aliases
    hgnc_symbol = StringField()
    aliases = ListField(StringField())
    
