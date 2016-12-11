from scout.models import (HgncTranscript, HgncGene)

def build_hgnc_transcript(transcript):
    """Build a HgncTranscript object

        Args:
            transcript(dict): Transcript information

        Returns:
            transcript_obj(HgncTranscript)
    """
    transcript_obj = HgncTranscript(
        ensembl_transcript_id = transcript['enst_id'],
        refseq_id = transcript['refseq'],
        start = transcript['start'],
        end = transcript['end'],
    )

    return transcript_obj

def build_hgnc_gene(gene):
    """Build a HgncGene

        Args:
            gene(dict): Gene information

        Returns:
            gene_obj(HgncGene)
    """
    gene_obj = HgncGene(
        hgnc_symbol = gene['hgnc_symbol'],
        ensembl_id = gene['ensembl_gene_id'],
        chromosome = gene['chromosome'],
        start = gene['start'],
        end = gene['end'],
    )

    gene_obj.hgnc_id = gene.get('hgnc_id')
    gene_obj.description = gene.get('description')
    gene_obj.aliases = gene.get('previous_symbols', [])
    gene_obj.entrez_id = gene.get('entrez_id')
    gene_obj.omim_ids = gene.get('omim_ids', [])
    gene_obj.pli_score = gene.get('pli_score')
    gene_obj.primary_transcripts = gene.get('ref_seq', [])
    gene_obj.ucsc_id = gene.get('ucsc_id')
    gene_obj.uniprot_ids = gene.get('uniprot_ids', [])
    gene_obj.vega_id = gene.get('vega_id')

    transcript_objs = []
    for transcript_id in gene.get('transcripts',[]):
        transcript = gene['transcripts'][transcript_id]
        transcript_objs.append(build_hgnc_transcript(transcript))

    if transcript_objs:
        gene_obj.transcripts = transcript_objs

    gene_obj.incomplete_penetrance = gene.get('incomplete_penetrance', False)
    gene_obj.ad = gene.get('ad', False)
    gene_obj.ar = gene.get('ar', False)
    gene_obj.xd = gene.get('xd', False)
    gene_obj.xr = gene.get('xr', False)
    gene_obj.x = gene.get('x', False)
    gene_obj.y = gene.get('y', False)

    return gene_obj
