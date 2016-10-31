from scout.constants import CONSERVATION

def parse_conservations(variant):
    """Parse the conservation predictors
    
        Args:
            variant(dict): A variant dictionary
        
        Returns:
            conservations(dict): A dictionary with the conservations
    """
    conservations = {}
    
    conservations['gerp'] = parse_conservation(
                                            variant, 
                                            'GERP++_RS_prediction_term'
                                        )
    conservations['phast'] = parse_conservation(
                                            variant,
                                            'phastCons100way_vertebrate_prediction_term'
                                        )
    conservations['phylop'] = parse_conservation(
                                            variant,
                                            'phyloP100way_vertebrate_prediction_term'
                                        )
    return conservations

def parse_conservation(variant, info_key):
    """Get the conservation prediction
    
        Args:
            variant(dict): A variant dictionary
            info_key(str)
        
        Returns:
            conservations(list): List of censervation terms
    """
    raw_annotation = variant['info_dict'].get(info_key)
    conservations = []
    
    if raw_annotation:
        for term in raw_annotation:
            if term in CONSERVATION:
                conservations.append(term)
    
    return conservations
