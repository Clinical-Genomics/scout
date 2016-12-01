from scout.models import Transcript

def build_transcript(transcript):
    """Build a mongoengine Transcript
    
        Args:
            transcript(dict)
    
        Returns:
            transcript_obj(Transcript)
    """

    transcript_obj = Transcript(
        transcript_id = transcript['transcript_id']
    )
    transcript_obj.hgnc_id = transcript['hgnc_id']

    transcript_obj.protein_id = transcript['protein_id']
    transcript_obj.sift_prediction = transcript['sift_prediction']
    transcript_obj.polyphen_prediction = transcript['polyphen_prediction']

    transcript_obj.swiss_prot = transcript['swiss_prot']
    transcript_obj.pfam_domain = transcript.get('pfam_domain')
    transcript_obj.prosite_profile = transcript.get('prosite_profile')
    transcript_obj.smart_domain = transcript.get('smart_domain')

    transcript_obj.biotype = transcript.get('biotype')

    transcript_obj.functional_annotations = transcript['functional_annotations']
    transcript_obj.region_annotations = transcript['region_annotations']

    transcript_obj.exon = transcript.get('exon')
    transcript_obj.intron = transcript.get('intron')
    transcript_obj.strand = transcript.get('strand')

    transcript_obj.coding_sequence_name = transcript['coding_sequence_name']
    transcript_obj.protein_sequence_name = transcript['protein_sequence_name']

    transcript_obj.is_canonical = transcript['is_canonical']

    return transcript_obj