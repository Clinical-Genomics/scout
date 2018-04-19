from __future__ import unicode_literals

from bson.objectid import ObjectId

hgnc_transcript = {
                'ensembl_transcript_id': str, # required
                'refseq_id': str,
                'start': int, # required
                'end': int, # required
                'is_primary': bool,
    }


hgnc_gene = {
                '_id': ObjectId(),
                'hgnc_id': int, # This is the hgnc id, required:
                'hgnc_symbol': str, # The primary symbol, required 
                'ensembl_id': str, # required
                'build': str, # '37' or '38', defaults to '37', required
                
                'chromosome': str, # required
                'start': int, # required
                'end': int, # required
                
                'description': str, # Gene description
                'aliases': list(), # Gene symbol aliases, includes hgnc_symbol, str
                'entrez_id': int,
                'omim_id': int,
                'pli_score': float,
                'primary_transcripts': list(), # List of refseq transcripts (str)
                'ucsc_id': str,
                'uniprot_ids': list(), # List of str
                'vega_id': str,
                
                # Inheritance information
                'inheritance_models': list(), # List of model names
                'incomplete_penetrance': bool, # Acquired from HPO
                
                # Phenotype information
                'phenotypes': list(), # List of dictionaries with phenotype information
    }
