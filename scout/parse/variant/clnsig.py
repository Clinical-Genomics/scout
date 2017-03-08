import logging

logger = logging.getLogger(__name__)

def parse_clnsig(variant):
    """Get the clnsig information

        We are only interested when clnsig = 5. So for each 5 we return the
        CLNSIG accesson number.

        Args:
            variant (dict): A Variant dictionary

        Returns:
            clnsig_accsessions(list): A list with clnsig accessions
    """
    clnsig_key = 'CLNSIG'
    accession_key = 'CLNACC'
    revstat_key = 'CLNREVSTAT'
    
    clnsig_annotation = variant['info_dict'].get(clnsig_key)
    accession_annotation = variant['info_dict'].get(accession_key)
    revstat_annotation = variant['info_dict'].get(revstat_key)

    clnsig_accsessions = []
    if clnsig_annotation:
        
        clnsig_annotation = clnsig_annotation[0].split('|')
        accession_annotation = accession_annotation[0].split('|')
        revstat_annotation = revstat_annotation[0].split('|')
        
        
        for i,annotation in enumerate(clnsig_annotation):
            clnsig_entry = {
                'value': int(annotation),
                'accession': accession_annotation[i],
                'revstat': revstat_annotation[i]
            }
            clnsig_accsessions.append(clnsig_entry)

    return clnsig_accsessions
