# -*- coding: utf-8 -*-
import logging

from scout.constants import SO_TERMS
from pprint import pprint as pp

LOG = logging.getLogger(__name__)

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
            hgnc_id = hgnc_id.split(':')[-1]
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
        # There are different keys for different versions of VEP
        # We only support version 90+
        thousandg_freqs = []
        gnomad_freqs = []
        try:
            # The keys for VEP v90+:
            # 'AF' or '1000GAF' - 1000G all populations combined
            # 'xxx_AF' - 1000G (or NHLBI-ESP) individual populations
            # 'gnomAD_AF' - gnomAD exomes, all populations combined
            # 'gnomAD_xxx_AF' - gnomAD exomes, individual populations
            # 'MAX_AF' - Max of all populations (1000G, gnomAD exomes, ESP)
            # https://www.ensembl.org/info/docs/tools/vep/vep_formats.html
            
            for key in entry:
                big_key = key.upper()
                
                #All frequencies endswith AF
                if not big_key.endswith('AF'):
                    continue
                
                if (big_key == 'AF' or big_key == '1000GAF'):
                    transcript['thousand_g_maf'] = float(entry[key])
                    continue
                
                if big_key == 'GNOMAD_AF':
                    transcript['gnomad_maf'] = float(entry[key])
                    continue

                if big_key == 'EXAC_MAX_AF':
                    transcript['exac_max'] = float(entry[key])
                    transcript['exac_maf'] = float(entry[key])
                    continue
                
                if 'GNOMAD' in big_key:
                    gnomad_freqs.append(float(entry[key]))
                
                else:
                    thousandg_freqs.append(float(entry[key]))
                
            if thousandg_freqs:
                transcript['thousandg_max'] = max(thousandg_freqs)

            if gnomad_freqs:
                transcript['gnomad_max'] = max(gnomad_freqs)
            
        except Exception as err:
            LOG.debug("Something went wrong when parsing frequencies")
            LOG.debug("Only splitted and normalised VEP v90+ is supported")

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

