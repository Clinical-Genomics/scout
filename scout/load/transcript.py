import logging

from pprint import pprint as pp

from click import progressbar
from pandas import DataFrame

from scout.parse.ensembl import (parse_ensembl_transcripts, parse_ensembl_transcript_request)
from scout.build.hgnc_gene import build_hgnc_transcript

LOG = logging.getLogger(__name__)

TRANSCRIPT_CATEGORIES = ['mrna', 'nc_rna', 'mrna_predicted']

def load_transcripts(adapter, transcripts_lines, build='37', ensembl_genes=None):
    """Load all the transcripts
    
    Transcript information is from ensembl.
    We need to collect information 
    
    Args:
        adapter(MongoAdapter)
        transcripts_lines(iterable): iterable with ensembl transcript lines
        build(str)
        ensembl_genes(dict): Existing ensembl genes
    
    Returns:
        loaded_transcripts(list): A list with all the loaded transcripts
    """
    loaded_transcripts = list()
    # Fetch all genes with ensemblid as keys
    ensembl_genes = ensembl_genes or adapter.ensembl_genes(build)
    LOG.info("Number of genes: {0}".format(len(ensembl_genes)))
    LOG.info("Number of genes: {0}".format(adapter.all_genes().count()))
    
    if isinstance(transcripts_lines, DataFrame):
        transcripts = parse_ensembl_transcript_request(transcripts_lines)
    else:
        transcripts = parse_ensembl_transcripts(transcripts_lines)
    
    transcripts_dict = {}
    genes = set()
    for tx in transcripts:
        tx_id = tx['ensembl_transcript_id']
        ens_gene_id = tx['ensembl_gene_id']
        gene_obj = ensembl_genes.get(ens_gene_id)
        if not gene_obj:
            LOG.debug("Gene %s does not exist in build %s" % (ens_gene_id, build))
            continue

        if not tx_id in transcripts_dict:
            transcripts_dict[tx_id] = {
                'chrom': tx['chrom'],
                'start': tx['transcript_start'],
                'end': tx['transcript_end'],
                'mrna': set(),
                'mrna_predicted': set(),
                'nc_rna': set(),
                'ensg_id': ens_gene_id,
                'transcript': tx_id,
                'hgnc_id': gene_obj['hgnc_id'],
                'primary_transcripts': set(gene_obj.get('primary_transcripts', [])),
            }

        if tx.get('refseq_mrna_predicted'):
            transcripts_dict[tx_id]['mrna_predicted'].add(tx['refseq_mrna_predicted'])
        if tx.get('refseq_mrna'):
            transcripts_dict[tx_id]['mrna'].add(tx['refseq_mrna'])
        if tx.get('refseq_ncrna'):
            transcripts_dict[tx_id]['nc_rna'].add(tx['refseq_ncrna'])
    
    LOG.info("Loading transcripts...")
    ref_seq_transcripts = 0
    nr_primary_transcripts = 0
    nr_transcripts = len(transcripts_dict)
    
    with progressbar(transcripts_dict.values(), label="Loading transcripts", length=nr_transcripts) as bar:
        for tx_data in bar:
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
                if identifiers:
                    intersection = identifiers.intersection(primary_transcripts)
                    if intersection:
                        refseq_identifier = intersection.pop()
                        tx_data['is_primary'] = True
                    else:
                        refseq_identifier = identifiers.pop()
                    break
            tx_data['refseq_id'] = refseq_identifier
            
            tx_obj = build_hgnc_transcript(tx_data, build)
            
            adapter.load_hgnc_transcript(tx_obj)
            
            loaded_transcripts.append(tx_obj)
            
            if tx_obj.get('refseq_id'):
                ref_seq_transcripts += 1
            if tx_obj.get('is_primary'):
                nr_primary_transcripts += 1
            
        
    
    LOG.info('Number of transcripts in build {0}: {1}'.format(build, nr_transcripts))
    LOG.info('Number of ref seq: %s' % ref_seq_transcripts)
    LOG.info('Number of primary: %s' % nr_primary_transcripts)
    
    return loaded_transcripts
    