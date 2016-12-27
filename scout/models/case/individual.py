from mongoengine import (StringField, IntField, ListField, EmbeddedDocument)
from scout.constants import ANALYSIS_TYPES


class Individual(EmbeddedDocument):
    """Represents an individual (sample) in a case (family)."""
    individual_id = StringField(required=True)
    display_name = StringField()
    sex = StringField()
    phenotype = IntField()
    father = StringField()
    mother = StringField()
    capture_kits = ListField(StringField())
    bam_file = StringField()
    analysis_type = StringField(choices=ANALYSIS_TYPES)

    @property
    def sex_human(self):
        """Transform sex string into human readable form."""
        # pythonic switch statement
        return {'1': 'male', '2': 'female'}.get(self.sex, 'unknown')

    @property
    def phenotype_human(self):
        """Transform phenotype integer into human readable form."""
        # pythonic switch statement
        terms = {-9: 'missing', 0: 'missing', 1: 'unaffected', 2: 'affected'}
        return terms.get(self.phenotype, 'undefined')

    def __unicode__(self):
        return self.display_name

    def __repr__(self):
        return "Individual(individual_id={0}, display_name={1})".format(
        self.individual_id, self.display_name)
