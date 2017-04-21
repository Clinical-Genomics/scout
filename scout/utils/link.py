import sys
import logging

from pprint import pprint as pp

from scout.parse.hgnc import parse_hgnc_genes
from scout.parse.ensembl import parse_ensembl_transcripts
from scout.parse.exac import parse_exac_genes
from scout.parse.hpo import get_incomplete_penetrance_genes
from scout.parse.omim import get_mim_genes

log = logging.getLogger(__name__)


def genes_by_alias(hgnc_genes):
    """Return a dictionary with hgnc symbols as keys

    Value of the dictionaries are information about the hgnc ids for a symbol.
    If the symbol is primary for a gene then 'true_id' will exist.
    A list of hgnc ids that the symbol points to is in ids.

    Args:
        hgnc_genes(dict): a dictionary with hgnc_id as key and gene info as value

    Returns:
        alias_genes(dict):
            {
                'hgnc_symbol':{
                    'true_id': int,
                    'ids': list(int)
                    }
            }
    """
    alias_genes = {}
    for hgnc_id in hgnc_genes:
        gene = hgnc_genes[hgnc_id]
        # This is the primary symbol:
        hgnc_symbol = gene['hgnc_symbol']

        for alias in gene['previous_symbols']:
            true_id = None
            if alias == hgnc_symbol:
                true_id = hgnc_id
            if alias in alias_genes:
                alias_genes[alias.upper()]['ids'].add(hgnc_id)
                if true_id:
                    alias_genes[alias.upper()]['true_id'] = hgnc_id
            else:
                alias_genes[alias.upper()] = {
                    'true_id': true_id,
                    'ids': set([hgnc_id])
                }

    return alias_genes

def add_ensembl_info(gene_info, ensembl_transcripts):
    """Add gene coordinates and transcripts to gene

    Parse and add all transcript information found in ensembl to gene.
    Add the gene coordinates.

    Args:
        gene_info(dict): dictionary with gene information
        ensembl_transcripts(list(dict)): list with transcript information

    """
    # Since there can be multiple transcripts with same ENSTID but different
    # refseq symbols we create a dictionary with transcript info
    transcripts_dict = {}
    gene_start = None
    gene_stop = None
    chromosome = None
    for transcript in ensembl_transcripts:
        parsed_transcript = {}
        refseq_identifier = None
        is_primary = False

        transcript_id = transcript['ensembl_transcript_id']
        gene_start = transcript['gene_start']
        gene_end = transcript['gene_end']
        chromosome = transcript['chrom']

        if transcript['refseq_mrna']:
            refseq_identifier = transcript['refseq_mrna']
        elif transcript['refseq_ncrna']:
            refseq_identifier = transcript['refseq_ncrna']
        elif transcript['refseq_mrna_predicted']:
            refseq_identifier = transcript['refseq_mrna_predicted']

        if refseq_identifier:
            if refseq_identifier in gene_info['ref_seq']:
                is_primary = True
            parsed_transcript['refseq'] = set([refseq_identifier])
        else:
            parsed_transcript['refseq'] = set()

        parsed_transcript['enst_id'] = transcript_id
        parsed_transcript['start'] = transcript['transcript_start']
        parsed_transcript['end'] = transcript['transcript_end']
        parsed_transcript['is_primary'] = is_primary

        if transcript_id in transcripts_dict:
            if is_primary:
                transcripts_dict[transcript_id]['is_primary'] = True
            if refseq_identifier:
                transcripts_dict[transcript_id]['refseq'].add(refseq_identifier)
        else:
            transcripts_dict[transcript_id] = parsed_transcript

    gene_info['chromosome'] = chromosome
    gene_info['start'] = gene_start
    gene_info['end'] = gene_end

    for transcript_id in transcripts_dict:
        transcript_info = transcripts_dict[transcript_id]
        transcript_info['refseq'] = list(transcript_info['refseq'])
        gene_info['transcripts'].append(transcripts_dict[transcript_id])



def link_genes(ensembl_lines, hgnc_lines, exac_lines, mim2gene_lines,
               genemap_lines, hpo_lines):
    """Gather information from different sources and return a gene dict

    Extract information collected from a number of sources and combine them
    into a gene dict with HGNC symbols as keys.

    hgnc_id works as the primary symbol and it is from this source we gather
    as much information as possible (hgnc_complete_set.txt)

    Coordinates are gathered from ensemble and the entries are linked from hgnc
    to ensembl via ENSGID.

    From exac the gene intolerance scores are collected, genes are linked to hgnc
    via hgnc symbol. This is a unstable symbol since they often change.


        Args:
            ensembl_lines(iterable(str))
            hgnc_lines(iterable(str))
            exac_lines(iterable(str))

        Yields:
            gene(dict): A dictionary with gene information
    """
    genes = {}
    log.info("Linking genes and transcripts")
    # HGNC genes are the main source, these define the gene dataset to use
    # Try to use as much information as possible from hgnc
    for hgnc_gene in parse_hgnc_genes(hgnc_lines):
        hgnc_id = hgnc_gene['hgnc_id']
        hgnc_gene['transcripts'] = []
        genes[hgnc_id] = hgnc_gene

    symbol_to_id = genes_by_alias(genes)
    # Parse and add the ensembl gene info
    all_genes = {'ensembl': {}, 'symbol': {}}
    for transcript in parse_ensembl_transcripts(ensembl_lines):
        ensg_symbol = transcript['hgnc_symbol']
        ensgid = transcript['ensembl_gene_id']
        for id_type, gene_id in [('symbol', ensg_symbol), ('ensembl', ensgid)]:
            if gene_id in all_genes[id_type]:
                all_genes[id_type][gene_id].append(transcript)
            else:
                all_genes[id_type][gene_id] = [transcript]

    log.info("Add ensembl info")
    # Add gene coordinates and transcript info for hgnc genes:
    for gene_info in genes.values():
        ensgid = gene_info['ensembl_gene_id']
        ensg_symbol = gene_info['hgnc_symbol']

        for id_type, gene_id in [('ensembl', ensgid), ('symbol', ensg_symbol)]:
            if gene_id:
                if gene_id in all_genes[id_type]:
                    add_ensembl_info(gene_info, all_genes[id_type][gene_id])
                    ensgid = 'ADDED'
                    break

    log.info("Add exac pli scores")
    for exac_gene in parse_exac_genes(exac_lines):
        hgnc_symbol = exac_gene['hgnc_symbol'].upper()
        pli_score = exac_gene['pli_score']

        if hgnc_symbol in symbol_to_id:
            hgnc_id_info = symbol_to_id[hgnc_symbol]

            # If we have the true id we know ot os correct
            if hgnc_id_info['true_id']:
                hgnc_id = hgnc_id_info['true_id']
                genes[hgnc_id]['pli_score'] = pli_score

            # Otherwise we loop over the ids and add pli score if it
            # is not already added
            else:
                for hgnc_id in hgnc_id_info['ids']:
                    gene_info = genes[hgnc_id]
                    if not gene_info.get('pli_score'):
                        gene_info['pli_score'] = pli_score

    log.info("Add omim info")
    omim_genes = get_mim_genes(genemap_lines, mim2gene_lines)
    for hgnc_symbol in omim_genes:
        omim_info = omim_genes[hgnc_symbol]
        inheritance = omim_info.get('inheritance', set())
        if hgnc_symbol in symbol_to_id:
            hgnc_id_info = symbol_to_id[hgnc_symbol]

            # If we have the true id we know it is correct
            if hgnc_id_info['true_id']:
                hgnc_id = hgnc_id_info['true_id']
                gene_info = genes[hgnc_id]

                # Update the omim id to the one found in omim
                gene_info['omim_id'] = omim_info['mim_number']

                gene_info['inheritance_models'] = list(inheritance)
                gene_info['phenotypes'] = omim_info.get('phenotypes', [])
            else:
                for hgnc_id in hgnc_id_info['ids']:
                    gene_info = genes[hgnc_id]
                    if not gene_info.get('omim_id'):
                        gene_info['omim_id'] = omim_info['mim_number']
                    if not gene_info.get('inheritance_models'):
                        gene_info['inheritance_models'] = list(inheritance)
                    if not gene_info.get('phenotypes'):
                        gene_info['phenotypes'] = omim_info.get('phenotypes', [])

    log.info("Add incomplete penetrance info")
    for hgnc_symbol in get_incomplete_penetrance_genes(hpo_lines):
        if hgnc_symbol in symbol_to_id:
            hgnc_id_info = symbol_to_id[hgnc_symbol]

            # If we have the true id we know ot os correct
            if hgnc_id_info['true_id']:
                hgnc_id = hgnc_id_info['true_id']
                genes[hgnc_id]['incomplete_penetrance'] = True

            # Otherwise we loop over the ids and add incomplete penetrance if it
            # is not already added
            else:
                for hgnc_id in hgnc_id_info['ids']:
                    gene_info = genes[hgnc_id]
                    if not 'incomplete_penetrance' in gene_info:
                        gene_info['incomplete_penetrance'] = True

    return genes
