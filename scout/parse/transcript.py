from .constants import SO_TERMS

def create_ensembl_to_refseq(variant):
    """Create a dictionary with ensembleids to refseq ids
    
        Args:
            variant(dict): A Variant dictionary
        
        Returns:
            conversion(dict): Dict that translate the ids
    """
    info_key = 'Ensembl_transcript_to_refseq_transcript'
    conversion = {}
    vcf_entry = variant['info_dict'].get(info_key, [])
    
    for gene_info in vcf_entry:
        #Genes are splitted from transcripts with ':'
        splitted_gene = gene_info.split(':')
        transcript_info = splitted_gene[1]
        for transcript in transcript_info.split('|'):
            splitted_transcript = transcript.split('>')
            if len(splitted_transcript) > 1:
                ensembl_id = splitted_transcript[0]
                refseq_ids = splitted_transcript[1].split('/')
                conversion[ensembl_id] = refseq_ids
    return conversion

def parse_disease_associated(variant):
    """Check if there are any manually annotated disease associated transcripts
    
        Args:
            variant(dict)
    
        Returns:
            disease_associated_transcripts(dict): {hgnc_symbol: (transcripts)}
    """
    disease_associated_transcripts = {}
    disease_transcripts = variant['info_dict'].get('Disease_associated_transcript')
    if disease_transcripts:
        for annotation in disease_transcripts:
            #Genes are separated with ':'
            annotation = annotation.split(':')
            if len(annotation) == 2:
                gene_id = annotation[0]
                transcript_ids = set(annotation[1].split('|'))

                if gene_id not in disease_associated_transcripts:
                    disease_associated_transcripts[gene_id] = set([
                        transcript_id.split('.')[0] for 
                        transcript_id in transcript_ids])
                else:
                    disease_associated_transcripts[gene_id].update(transcript_ids)
    return disease_associated_transcripts

def parse_transcripts(variant):
    """Create a list of mongo engine transcript objects
    
        Args:
            variant(dict)
        
        Returns:
            transcripts(list(Transcript))
    """
    ensembl_to_refseq = create_ensembl_to_refseq(variant)
    disease_associated_transcripts = parse_disease_associated(variant)
    transcripts = []

    for vep_entry in variant['vep_info'].get(variant['ALT'], []):
        transcript = {}
        # There can be several functional annotations for one variant
        functional_annotations = vep_entry.get('Consequence', '').split('&')
        transcript['functional_annotations'] = functional_annotations
        # Get the transcript id
        transcript_id = vep_entry.get('Feature', '').split(':')[0]
        transcript['transcript_id'] = transcript_id
        
        transcript['refseq_ids'] = ensembl_to_refseq.get(transcript_id, [])
        
        # Add the hgnc gene identifier
        transcript['hgnc_symbol'] = vep_entry.get('SYMBOL', '').split('.')[0]

        transcript['is_disease_associated'] = False
        disease_transcripts = disease_associated_transcripts.get(transcript['hgnc_symbol'], set())
        for refseq_id in transcript['refseq_ids']:
            if refseq_id in disease_transcripts:
                transcript['is_disease_associated'] = True

        # Add the ensembl gene identifier
        transcript['ensembl_id'] = vep_entry.get('Gene', '')
      
        ########### Fill it with the available information ###########
      
        ### Protein specific annotations ###
      
        ## Protein ID ##
        transcript['protein_id'] = vep_entry.get('ENSP')
        transcript['polyphen_prediction'] = vep_entry.get('PolyPhen')
        transcript['sift_prediction'] = vep_entry.get('SIFT')
        transcript['swiss_prot'] = vep_entry.get('SWISSPROT')

        if vep_entry.get('DOMAINS', None):
            pfam_domains = vep_entry['DOMAINS'].split('&')
        
            for annotation in pfam_domains:
                annotation = annotation.split(':')
                domain_name = annotation[0]
                domain_id = annotation[1]
                if domain_name == 'Pfam_domain':
                    transcript['pfam_domain'] = domain_id
                elif domain_name == 'PROSITE_profiles':
                    transcript['prosite_profile'] = domain_id
                elif domain_name == 'SMART_domains':
                    transcript['smart_domain'] = domain_id

        coding_sequence_entry = vep_entry.get('HGVSc', '').split(':')
        protein_sequence_entry = vep_entry.get('HGVSp', '').split(':')
      
        coding_sequence_name = None
        if len(coding_sequence_entry) > 1:
            coding_sequence_name = coding_sequence_entry[-1]
      
        transcript['coding_sequence_name'] = coding_sequence_name
      
        protein_sequence_name = None
        if len(protein_sequence_entry) > 1:
            protein_sequence_name = protein_sequence_entry[-1]
      
        transcript['protein_sequence_name'] = protein_sequence_name
      
        transcript['biotype'] = vep_entry.get('BIOTYPE')
      
        transcript['exon'] = vep_entry.get('EXON')
        transcript['intron'] = vep_entry.get('INTRON')
        
        if vep_entry.get('STRAND'):
            if vep_entry['STRAND'] == '1':
                transcript['strand'] = '+'
            elif vep_entry['STRAND'] == '-1':
                transcript['strand'] = '-'
        else:
            transcript['strand'] = None
            
        functional = []
        regional = []
        for annotation in functional_annotations:
            functional.append(annotation)
            regional.append(SO_TERMS[annotation]['region'])
      
        transcript['functional_annotations'] = functional
        transcript['region_annotations'] = regional
        
        transcript['is_canonical'] = (vep_entry.get('CANONICAL') == 'YES') 
        
        
        transcripts.append(transcript)
    
    return transcripts 
