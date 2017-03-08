# -*- coding: utf-8 -*-
from scout.constants import SO_TERMS

def parse_transcripts(variant):
    """Create a list of mongo engine transcript objects

        Args:
            variant(dict)

        Returns:
            transcripts(list(Transcript))
    """
    transcripts = []

    for allele in variant['vep_info']:
        for vep_entry in variant['vep_info'][allele]:
            transcript = {}
            # There can be several functional annotations for one variant
            functional_annotations = vep_entry.get('Consequence', '').split('&')
            transcript['functional_annotations'] = functional_annotations
            # Get the transcript id
            transcript_id = vep_entry.get('Feature', '').split(':')[0]
            transcript['transcript_id'] = transcript_id

            # Add the hgnc gene identifiers
            hgnc_id = vep_entry.get('HGNC_ID')
            if hgnc_id:
                transcript['hgnc_id'] = int(hgnc_id)
            else:
                transcript['hgnc_id'] = None

            ########### Fill it with the available information ###########

            ### Protein specific annotations ###

            ## Protein ID ##
            transcript['protein_id'] = vep_entry.get('ENSP')
            transcript['polyphen_prediction'] = vep_entry.get('PolyPhen') or 'unknown'
            transcript['sift_prediction'] = vep_entry.get('SIFT') or 'unknown'
            transcript['swiss_prot'] = vep_entry.get('SWISSPROT') or 'unknown'

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
