
def build_hgnc_transcript(transcript_info, primary_transcripts):
    """Build a hgnc_transcript object

        Args:
            transcript_info(dict): Transcript information
            primary_transcripts(list(str)): The primary transcripts

        Returns:
            transcript_obj(HgncTranscript)
            {
                ensembl_transcript_id: str, required
                refseq_id: str,
                start: int, required
                end: int, required
                is_primary: bool
            }
    """
    try:
        transcript_obj = {'ensembl_transcript_id':transcript_info['enst_id']}
    except KeyError:
        raise KeyError("Transcript has to have ensembl id")
    transcript_obj['is_primary'] = False
    
    refseq_id = transcript_info.get('refseq')
    if refseq_id:
        transcript_obj['refseq_id'] = refseq_id
        if refseq_id in primary_transcripts:
            transcript_obj['is_primary'] = True
    
    try:
        transcript_obj['start'] = int(transcript_info['start'])
    except KeyError:
        raise KeyError("Transcript has to have start")
    except TypeError:
        raise TypeError("Transcript start has to be integer")

    try:
        transcript_obj['end'] = int(transcript_info['end'])
    except KeyError:
        raise KeyError("Transcript has to have end")
    except TypeError:
        raise TypeError("Transcript end has to be integer")

    return transcript_obj

def build_hgnc_gene(gene_info):
    """Build a hgnc_gene object

        Args:
            gene_info(dict): Gene information

        Returns:
            gene_obj(dict)
    
            {
                hgnc_id: Int # This is the hgnc id, required
                
                hgnc_symbol: str # The primary symbol, required 
                ensembl_id: str, required
                build: str, '37' or '38', defaults to '37'
                
                chromosome: str, required
                start: int, required
                end: int, required
                
                description: str
                aliases: list(str)
                entrez_id: int
                omim_ids: list(int)
                pli_score: float
                primary_transcripts: list(str)
                ucsc_id: str
                uniprot_ids: list(str)
                vega_id: str
                transcripts: list((dict))
                
                # Inheritance information
                incomplete_penetrance: bool
                ar: bool, defaults to False
                ad: bool, defaults to False
                mt: bool, defaults to False
                xr: bool, defaults to False
                xd: bool, defaults to False
                x: bool , defaults to False
                y: bool , defaults to False
        
    }
    """
    try:
        gene_obj = {'hgnc_id':int(gene_info['hgnc_id'])}
    except KeyError as err:
        raise KeyError("Gene has to have a hgnc_id")
    except ValueError as err:
        raise ValueError("hgnc_id has to be integer")
    
    try:
        gene_obj['hgnc_symbol'] = gene_info['hgnc_symbol']
    except KeyError as err:
        raise KeyError("Gene has to have a hgnc_symbol")

    try:
        gene_obj['ensembl_id'] = gene_info['ensembl_gene_id']
    except KeyError as err:
        raise KeyError("Gene has to have a ensembl_id")

    try:
        gene_obj['chromosome'] = gene_info['chromosome']
    except KeyError as err:
        raise KeyError("Gene has to have a chromosome")
    
    try:
        gene_obj['start'] = int(gene_info['start'])
    except KeyError as err:
        raise KeyError("Gene has to have a start position")
    except TypeError as err:
        raise TypeError("Gene start has to be a integer")

    try:
        gene_obj['end'] = int(gene_info['end'])
    except KeyError as err:
        raise KeyError("Gene has to have a end position")
    except TypeError as err:
        raise TypeError("Gene end has to be a integer")

    gene_obj['build'] = gene_info.get('build', '37')
    gene_obj['description'] = gene_info.get('description')
    gene_obj['aliases'] = gene_info.get('previous_symbols', [])
    gene_obj['entrez_id'] = gene_info.get('entrez_id')
    gene_obj['omim_ids'] = gene_info.get('omim_ids', [])
    try:
        gene_obj['pli_score'] = float(gene_info.get('pli_score'))
    except TypeError as err:
        gene_obj['pli_score'] = None
    
    primary_transcripts = gene_info.get('ref_seq', [])
    gene_obj['primary_transcripts'] = primary_transcripts
    gene_obj['ucsc_id'] = gene_info.get('ucsc_id')
    gene_obj['uniprot_ids'] = gene_info.get('uniprot_ids', [])
    gene_obj['vega_id'] = gene_info.get('vega_id')

    transcript_objs = []
    for transcript_id in gene_info.get('transcripts',[]):
        transcript_info = gene_info['transcripts'][transcript_id]
        transcript_objs.append(
            build_hgnc_transcript(transcript_info, primary_transcripts))

    gene_obj['transcripts'] = transcript_objs

    gene_obj['incomplete_penetrance'] = gene_info.get('incomplete_penetrance', False)
    gene_obj['ad'] = gene_info.get('ad', False)
    gene_obj['ar'] = gene_info.get('ar', False)
    gene_obj['xd'] = gene_info.get('xd', False)
    gene_obj['xr'] = gene_info.get('xr', False)
    gene_obj['x'] = gene_info.get('x', False)
    gene_obj['y'] = gene_info.get('y', False)

    return gene_obj
