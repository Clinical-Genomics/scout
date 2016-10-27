from __future__ import unicode_literals

from mongoengine import (Document, StringField, ListField, EmbeddedDocument,
                         IntField, FloatField, EmbeddedDocumentField, 
                         BooleanField)

class HgncAlias(Document):
    #This works like a dictionary where hgnc_symbol is the correct id and
    #values are all aliases
    hgnc_symbol = StringField(required=True)
    aliases = ListField(StringField())


class HgncTranscript(EmbeddedDocument):
    ensembl_transcript_id = StringField(required=True, unique=True)
    refseq_id = StringField(required=True)
    start = IntField(required=True)
    end = IntField(required=True)
    

class HgncGene(Document):
    #This works like a dictionary where hgnc_symbol is the correct id and
    #values are all aliases
    hgnc_symbol = StringField(required=True, unique=True)
    ensembl_id = StringField(required=True)
    
    hgnc_id = IntField()
    
    chromosome = StringField(required=True)
    start = IntField(required=True)
    end = IntField(required=True)
    
    description = StringField()
    aliases = ListField(StringField())
    entrez_id = IntField()
    omim_ids = ListField(IntField())
    pli_score = FloatField()
    primary_transcript = StringField()
    ucsc_id = StringField()
    uniprot_ids = ListField(StringField())
    vega_id = StringField()
    transcripts = ListField(EmbeddedDocumentField(HgncTranscript))
    
    #Inheritance information
    incomplete_penetrance = BooleanField()
    ar = BooleanField()
    ad = BooleanField()
    mt = BooleanField()
    xr = BooleanField()
    xd = BooleanField()
    x = BooleanField()
    y = BooleanField()
    
    @property
    def hgnc_link(self):
        """Link to gene in HGNC"""
        url_template = ("http://www.genenames.org/cgi-bin/gene_symbol_report"\
                        "?hgnc_id=HGNC:{}")
        return url_template.format(self.hgnc_id)

    @property
    def genecards_link(self):
        """Link to gene in genecards.org"""
        url_template = ("http://www.genecards.org/cgi-bin/carddisp.pl?gene={}")
        return url_template.format(self.hgnc_symbol)
        
    meta = {
        'index_background': True,
        'indexes':[
            'hgnc_id',
            ('chromosome' ,'+start', '+end'),
        ]
    }
    