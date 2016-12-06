

def get_correct_gene(hgnc_symbol, genes):
    """Check which of the genes in query result that is the correct one
        
        If there result is ambigous, that is if non of the genes have the hgnc 
        symbol as the primary identifier and two or more genes have the symbol
        as an alias, return all of those results.
    
        Args:
            hgnc_symbol(str)
            genes(iterable[Gene])
            
    """
    for gene in genes:
        #if one of the gene matches the hgnc symbol return the correct one
        if hgnc_symbol == gene['hgnc_symbol']:
            return gene
    
    