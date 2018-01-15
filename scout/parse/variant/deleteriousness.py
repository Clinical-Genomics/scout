
def parse_cadd(variant, transcripts):
    """Check if the cadd phred score is annotated"""
    cadd = 0
    cadd_keys = ['CADD', 'CADD_PHRED']
    for key in cadd_keys:
        cadd = variant.INFO.get(key, 0)
        if cadd:
            return float(cadd)
    
    for transcript in transcripts:
        cadd_entry = transcript.get('cadd')
        if (cadd_entry and cadd_entry > cadd):
            cadd = cadd_entry
    
    return cadd
    
def parse_spidex(variant):
    """Get SPIDEX annotation, translate internally to human readable string."""
    
    spidex = variant.INFO.get('SPIDEX')

    if spidex is None:
        spidex_human = 'not_reported'
    elif abs(spidex) < 1:
        spidex_human = 'low'
    elif abs(spidex) < 2:
        spidex_human = 'medium'
    else:
        spidex_human = 'high'
    
    return (spidex, spidex_human)

