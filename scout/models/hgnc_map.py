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
    ensembl_transcript_id = StringField(required=True)
    refseq_id = StringField()
    start = IntField(required=True)
    end = IntField(required=True)

    @property
    def refseq_link(self):
        return "http://www.ncbi.nlm.nih.gov/nuccore/{}".format(self.refseq_id)


class HgncGene(Document):
    hgnc_id = IntField(primary_key=True)

    hgnc_symbol = StringField(required=True, unique=True)
    ensembl_id = StringField(required=True)

    chromosome = StringField(required=True)
    start = IntField(required=True)
    end = IntField(required=True)

    description = StringField()
    aliases = ListField(StringField())
    entrez_id = IntField()
    omim_ids = ListField(IntField())
    pli_score = FloatField()
    primary_transcripts = ListField(StringField())
    ucsc_id = StringField()
    uniprot_ids = ListField(StringField())
    vega_id = StringField()
    transcripts = ListField(EmbeddedDocumentField(HgncTranscript))

    # Inheritance information
    incomplete_penetrance = BooleanField()
    ar = BooleanField()
    ad = BooleanField()
    mt = BooleanField()
    xr = BooleanField()
    xd = BooleanField()
    x = BooleanField()
    y = BooleanField()

    @property
    def inheritance(self):
        """Return a list of inheritance information."""
        return [('AR', self.ar), ('AD', self.ad), ('MT', self.mt),
                ('XR', self.xr), ('XD', self.xd), ('X', self.x), ('Y', self.y)]

    @property
    def expected_inheritance(self):
        """Return all models that are expected."""
        for model, is_expected in self.inheritance:
            if is_expected:
                yield model

    @property
    def position(self):
        return "{this.chromosome}:{this.start}-{this.end}".format(this=self)

    @property
    def hgnc_link(self):
        """Link to gene in HGNC"""
        url_template = ("http://www.genenames.org/cgi-bin/gene_symbol_report"
                        "?hgnc_id=HGNC:{}")
        return url_template.format(self.hgnc_id)

    @property
    def genecards_link(self):
        """Link to gene in genecards.org"""
        url_template = ("http://www.genecards.org/cgi-bin/carddisp.pl?gene={}")
        return url_template.format(self.hgnc_symbol)

    @property
    def entrez_link(self):
        """Link to gene in ncbi.org"""
        url_template = ("https://www.ncbi.nlm.nih.gov/gene/{}")
        return url_template.format(self.entrez_id)

    @property
    def ensembl_link(self):
        """Link to gene in ensembl.org"""
        url_template = ("http://www.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={}")
        return url_template.format(self.ensembl_id)

    @property
    def vega_link(self):
        """Link to gene in sangers vega database"""
        url_template = ("http://vega.sanger.ac.uk/Homo_sapiens/Gene/Summary?db=core;g={}")
        return url_template.format(self.vega_id)

    @property
    def ucsc_link(self):
        """Link to gene in ucsc database"""
        url_template = ("http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&"
                        "hgg_chrom=none&hgg_type=knownGene&hgg_gene={}")
        return url_template.format(self.ucsc_id)

    @property
    def reactome_link(self):
        url_template = ("http://www.reactome.org/content/query?q={}&"
                        "species=Homo+sapiens&species=Entries+without+species&"
                        "cluster=true")
        return url_template.format(self.ensembl_id)

    @property
    def hpa_link(self):
        return "http://www.proteinatlas.org/search/{}".format(self.ensembl_id)

    @property
    def string_link(self):
        return ("http://string-db.org/newstring_cgi/show_network_section."
                "pl?identifier={}".format(self.ensembl_id))

    @property
    def expression_atlas_link(self):
        url_template = ("https://www.ebi.ac.uk/gxa/genes/{}?"
                        "bs=%7B%22homo+sapiens%22%3A%7B%22CELL_LINE%22%3Atrue"
                        "%2C%22ORGANISM_PART%22%3Atrue%7D%7D&ds=%7B%22species"
                        "%22%3A%7B%22homo+sapiens%22%3Atrue%7D%7D")
        return url_template.format(self.ensembl_id)


    def __repr__(self):
        return ("HgncGene(hgnc_id={this.hgnc_id},hgnc_symbol={this.hgnc_symbol})".format(this=self))

    def __str__(self):
        return ("HgncGene(hgnc_id={this.hgnc_id},hgnc_symbol={this.hgnc_symbol}"
                ",aliases={this.aliases})".format(this=self))

    meta = {
        'index_background': True,
        'indexes':[
            '$hgnc_symbol',
            'aliases',
            ('chromosome' ,'+start', '+end'),
        ]
    }
