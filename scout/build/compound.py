from scout.models import Compound

def build_compound(compound):
    """Build a mongoengine Compound object
    
        Args:
            compound(dict)
    
        Returns:
            compound_obj(Compound)
    """
    # This must be the document_id for this variant
    variant = StringField(required=True)
    # This is the variant id
    display_name = StringField(required=True)
    combined_score = FloatField(required=True)
    
    compound_obj = Compound(
        variant = compound['variant'],
        display_name = compound['display_name'],
        combined_score = compound['score']
    )
    
    return compound_obj