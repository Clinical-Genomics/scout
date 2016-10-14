from scout.models import Compound

def build_compound(compound):
    """Build a mongoengine Compound object
    
        Args:
            compound(dict)
    
        Returns:
            compound_obj(Compound)
    """
    
    compound_obj = Compound(
        variant = compound['variant'],
        display_name = compound['display_name'],
        combined_score = compound['score']
    )
    
    return compound_obj