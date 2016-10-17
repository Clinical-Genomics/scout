def get_omim_gene_ids(variant):
    """Get the mim ids for the genes
    
        Args:
            variant (dict): A Variant dictionary
        
        Returns:
            mim_ids(dict): hgnc_id as key and mim id as value
    """
    vcf_key = 'OMIM_morbid'
    vcf_entry = variant['info_dict'].get(vcf_key, [])
    
    mim_ids = {}
    for annotation in vcf_entry:
        if annotation:
            splitted_record = annotation.split(':')
            try:
                hgnc_symbol = splitted_record[0]
                omim_term = int(splitted_record[1])
                mim_ids[hgnc_symbol] = omim_term
            except (ValueError, KeyError):
                pass
    return mim_ids

def get_omim_phenotype_ids(variant):
    """Get the mim phenotype ids for the genes
    
        Args:
            variant (dict): A Variant dictionary
        
        Returns:
            phenotype_mim_ids(dict): hgnc_id as key and mim id as value
    """
    vcf_key = 'Phenotypic_disease_model'
    vcf_entry = variant['info_dict'].get(vcf_key, [])
    
    phenotype_mim_ids = {}
    for annotation in vcf_entry:
        if annotation:
            mim_phenotype = {}
            splitted_annotation = annotation.split(':')
            hgnc_symbol = splitted_annotation[0]
            splitted_entry = splitted_annotation[1].split('|')
            
            for record in splitted_entry:
                splitted_record = record.split('>')
                phenotype_id = splitted_record[0]
                inheritance_patterns = []
                if len(splitted_record) > 1:
                    inheritance_patterns = splitted_record[1].split('/')
          
                mim_phenotype['phenotype_id'] = phenotype_id
                mim_phenotype['disease_models'] = inheritance_patterns
                
                if hgnc_symbol in phenotype_mim_ids:
                    phenotype_mim_ids[hgnc_symbol].append(mim_phenotype)
                else:
                    phenotype_mim_ids[hgnc_symbol] = [mim_phenotype]
                    
    return phenotype_mim_ids
