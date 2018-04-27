import logging

from pprint import pprint as pp

from click import progressbar
from pandas import DataFrame

from scout.parse.ensembl import (parse_ensembl_transcripts, parse_ensembl_transcript_request)
from scout.build.genes.transcript import build_transcript

LOG = logging.getLogger(__name__)

TRANSCRIPT_CATEGORIES = ['mrna', 'nc_rna', 'mrna_predicted']

def load_transcripts(adapter, transcripts_lines, build='37', ensembl_genes=None):
    """Load all the transcripts
    
    Transcript information is from ensembl.
    
    Args:
        adapter(MongoAdapter)
        transcripts_lines(iterable): iterable with ensembl transcript lines
        build(str)
        ensembl_genes(dict): Existing ensembl genes
    
    Returns:
        transcript_objs(list): A list with all transcript objects
    """
    # Fetch all genes with ensemblid as keys
    ensembl_genes = ensembl_genes or adapter.ensembl_genes(build)
    LOG.info("Number of genes: {0}".format(len(ensembl_genes)))

    # Parse the transcripts, we need to check if it is a request or a file handle
    if isinstance(transcripts_lines, DataFrame):
        transcripts = parse_ensembl_transcript_request(transcripts_lines)
    else:
        transcripts = parse_ensembl_transcripts(transcripts_lines)

    # Since there can be multiple lines with information about the same transcript
    # we store transcript information in a dictionary for now
    transcripts_dict = {}
    # Loop over the parsed transcripts
    for tx in transcripts:
        tx_id = tx['ensembl_transcript_id']
        ens_gene_id = tx['ensembl_gene_id']
        gene_obj = ensembl_genes.get(ens_gene_id)
        # If the gene is non existing in scout we skip the transcript
        if not gene_obj:
            LOG.debug("Gene %s does not exist in build %s", ens_gene_id, build)
            continue

        # Check if the transcript has been added
        # If not, create a new transcript
        if not tx_id in transcripts_dict:
            tx_info = {
                'chrom': tx['chrom'],
                'start': tx['transcript_start'],
                'end': tx['transcript_end'],
                'mrna': set(),
                'mrna_predicted': set(),
                'nc_rna': set(),
                'ensg_id': ens_gene_id,
                'transcript': tx_id,
                'hgnc_id': gene_obj['hgnc_id'],
                # Primary transcript information is collected from HGNC
                'primary_transcripts': set(gene_obj.get('primary_transcripts', [])),
            }
            transcripts_dict[tx_id] = tx_info

        # Add the ref seq information
        if tx.get('refseq_mrna_predicted'):
            tx_info['mrna_predicted'].add(tx['refseq_mrna_predicted'])
        if tx.get('refseq_mrna'):
            tx_info['mrna'].add(tx['refseq_mrna'])
        if tx.get('refseq_ncrna'):
            tx_info['nc_rna'].add(tx['refseq_ncrna'])
    
    ref_seq_transcripts = 0
    nr_primary_transcripts = 0
    nr_transcripts = len(transcripts_dict)
    
    transcript_objs = []
    
    with progressbar(transcripts_dict.values(), label="Building transcripts", length=nr_transcripts) as bar:
        for tx_data in bar:
            
            #################### Get the correct refseq identifier ####################
            # We need to decide one refseq identifier for each transcript, if there are any to choose 
            # from. The algorithm is as follows:
            # If these is ONE mrna this is choosen
            # If there are several mrna the one that is in 'primary_transcripts' is choosen
            # Else one is choosen at random
            # The same follows for the other categories where nc_rna has precedense over mrna_predicted
            tx_data['is_primary'] = False
            primary_transcripts = tx_data['primary_transcripts']
            refseq_identifier = None
            for category in TRANSCRIPT_CATEGORIES:
                identifiers = tx_data[category]
                if not identifiers:
                    continue
                
                intersection = identifiers.intersection(primary_transcripts)
                ref_seq_transcripts += 1
                if intersection:
                    refseq_identifier = intersection.pop()
                    tx_data['is_primary'] = True
                    nr_primary_transcripts += 1
                else:
                    refseq_identifier = identifiers.pop()
                # If there was refseq identifiers we break the loop
                break

            if refseq_identifier:
                tx_data['refseq_id'] = refseq_identifier
            ####################  ####################  ####################

            # Build the transcript object
            tx_obj = build_transcript(tx_data, build)
            transcript_objs.append(tx_obj)

    # Load all transcripts
    LOG.info("Loading transcripts...")
    if len(transcript_objs) > 0:
        adapter.load_transcript_bulk(transcript_objs)

    LOG.info('Number of transcripts in build %s: %s', build, nr_transcripts)
    LOG.info('Number of transcripts with refseq identifier: %s', ref_seq_transcripts)
    LOG.info('Number of primary transcripts: %s', nr_primary_transcripts)

    return transcript_objs
    