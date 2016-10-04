from mongoengine import (Document, EmbeddedDocument, EmbeddedDocumentField,
                         FloatField, IntField, StringField, ReferenceField,
                         BooleanField)


class StructuralVariant(Document):
    
    document_id = StringField(primary_key=True)
    variant_id = StringField(required=True)
    display_name = StringField(required=True)
    
    institute = ReferenceField('Institute', required=True)
    case = ReferenceField('Case', required=True)
    
    # The variant can be either research or clinical.
    # For research variants we display all the available information while
    # the clinical variants have limited annotation fields.
    variant_type = StringField(required=True,
                               choices=('research', 'clinical'))
    
    chromosome = StringField(required=True)
    start = IntField(required=True)
    end = IntField(required=True)
    
    sv_type = StringField(required=True, 
                          choises=('DEL', 'INS', 'DUP', 'INV', 'CNV'))
    
    sv_len = IntField(required=True)
    
    imprecise = BooleanField(required=True)
    
    thousand_genomes_frequency = FloatField()

