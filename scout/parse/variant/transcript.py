# -*- coding: utf-8 -*-
from scout.constants import SO_TERMS
from pprint import pprint as pp

def parse_transcripts(raw_transcripts, allele=None):
    """Parse transcript information from VCF variants

    Args:
        raw_transcripts(iterable(dict)): An iterable with raw transcript 
                                         information

    Yields:
        transcript(dict) A dictionary with transcript information
    """
    for entry in raw_transcripts:
        transcript = {}
        # There can be several functional annotations for one variant
        functional_annotations = entry.get('Consequence', '').split('&')
        transcript['functional_annotations'] = functional_annotations
        # Get the transcript id (ensembl gene id)
        transcript_id = entry.get('Feature', '').split(':')[0]
        transcript['transcript_id'] = transcript_id

        # Add the hgnc gene identifiers
        hgnc_id = entry.get('HGNC_ID')
        if hgnc_id:
            transcript['hgnc_id'] = int(hgnc_id)
        else:
            transcript['hgnc_id'] = None

        hgnc_symbol = entry.get('SYMBOL')
        if hgnc_symbol:
            transcript['hgnc_symbol'] = hgnc_symbol
        else:
            transcript['hgnc_symbol'] = None

        ########### Fill it with the available information ###########

        ### Protein specific annotations ###

        ## Protein ID ##
        transcript['protein_id'] = entry.get('ENSP')
        
        polyphen_prediction = entry.get('PolyPhen')
        if polyphen_prediction:
            prediction_term = polyphen_prediction.split('(')[0]
        else:
            prediction_term = 'unknown'
        transcript['polyphen_prediction'] = prediction_term

        sift_prediction = entry.get('SIFT')
        if sift_prediction:
            prediction_term = sift_prediction.split('(')[0]
        else:
            prediction_term = 'unknown'

        transcript['sift_prediction'] = prediction_term
        
        transcript['swiss_prot'] = entry.get('SWISSPROT') or 'unknown'

        if entry.get('DOMAINS', None):
            pfam_domains = entry['DOMAINS'].split('&')

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

        coding_sequence_entry = entry.get('HGVSc', '').split(':')
        protein_sequence_entry = entry.get('HGVSp', '').split(':')

        coding_sequence_name = None
        if len(coding_sequence_entry) > 1:
            coding_sequence_name = coding_sequence_entry[-1]

        transcript['coding_sequence_name'] = coding_sequence_name

        protein_sequence_name = None
        if len(protein_sequence_entry) > 1:
            protein_sequence_name = protein_sequence_entry[-1]

        transcript['protein_sequence_name'] = protein_sequence_name

        transcript['biotype'] = entry.get('BIOTYPE')

        transcript['exon'] = entry.get('EXON')
        transcript['intron'] = entry.get('INTRON')

        if entry.get('STRAND'):
            if entry['STRAND'] == '1':
                transcript['strand'] = '+'
            elif entry['STRAND'] == '-1':
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

        # Check if the transcript is marked cannonical by vep
        transcript['is_canonical'] = (entry.get('CANONICAL') == 'YES')
        
        # Check if the CADD score is available on transcript level
        cadd_phred = entry.get('CADD_PHRED')
        if cadd_phred:
            transcript['cadd'] = float(cadd_phred)

        # Check frequencies
        exac_frequencies = []
        thousandg_frequencies = []
        for key in entry:
            if key.endswith('MAF'):
                # If the frequency starts with 'ExAC' we know it is a exac freq
                splitted_entry = entry[key].split(':')
                if splitted_entry[0] == allele:
                    value = float(splitted_entry[1])
                    if value > 0:
                        if key.startswith('ExAC'):
                            exac_frequencies.append(value)
                # Otherwise we know it is a 1000G frequency
                        else:
                            thousandg_frequencies.append(value)

        if exac_frequencies:
            transcript['exac_maf'] = sum(exac_frequencies)/len(exac_frequencies)
            transcript['exac_max'] = max(exac_frequencies)

        if thousandg_frequencies:
            transcript['thousand_g_maf'] = sum(thousandg_frequencies)/len(thousandg_frequencies)
            transcript['thousandg_max'] = max(thousandg_frequencies)

        clinsig = entry.get('CLIN_SIG')
        if clinsig:
            transcript['clinsig'] = clinsig.split('&')
        
        transcript['dbsnp'] = []
        transcript['cosmic'] = []
        variant_ids = entry.get('Existing_variation')
        if variant_ids:
            for variant_id in variant_ids.split('&'):
                if variant_id.startswith('rs'):
                    transcript['dbsnp'].append(variant_id)
                elif variant_id.startswith('COSM'):
                    transcript['cosmic'].append(int(variant_id[4:]))

        yield transcript

