import os
import logging

from pprint import pprint as pp

import click

from scout.utils.requests import (fetch_hgnc, fetch_mim_files, fetch_exac_constraint, 
fetch_ensembl_genes, fetch_ensembl_transcripts, fetch_hpo_files, fetch_hpo_genes, fetch_hpo_terms,)
from scout.parse.hgnc import parse_hgnc_line
from scout.parse.omim import parse_genemap2, parse_mim2gene
from scout.parse.exac import parse_exac_genes
from scout.parse.ensembl import (parse_ensembl_gene_request, parse_ensembl_transcript_request)

from . import (hgnc_reduced_path, genemap2_reduced_path, mim2gene_reduced_path, exac_reduced_path, 
genes37_reduced_path, genes38_reduced_path, transcripts37_reduced_path, transcripts38_reduced_path,
hpogenes_reduced_path, hpoterms_reduced_path, hpo_phenotype_to_terms_reduced_path)


LOG = logging.getLogger(__name__)

def get_reduced_hpo_terms(hpo_terms):
    """Return a reduced version of the hpo terms
    
    Args:
        hpo_terms(set(str)): Set of choosen terms that should be included

    Yields:
        hpo_line: A line with hpo information
    """
    hpo_lines = fetch_hpo_terms()
    
    begining = True
    
    term_lines = []
    # We want to keep the header lines
    keep = True
    
    nr_terms = 0
    nr_kept = 0

    for line in hpo_lines:
        
        # When we encounter a new term we yield all lines of the previous term
        if line.startswith('[Term]'):
            nr_terms += 1
            if keep:
                nr_kept += 1
                for hpo_line in term_lines:
                    yield hpo_line

            keep = False
            term_lines = []
        
        elif line.startswith('id'):
            hpo_id = line[4:]
            if hpo_id in hpo_terms:
                keep = True
        
        term_lines.append(line)
        

    if keep:
        for hpo_line in term_lines:
            yield hpo_line
    
    LOG.info("Nr of terms in file %s", nr_terms)
    LOG.info("Nr of terms kept: %s", nr_kept)
        

def remove_file(path):
    """Check if a file exists and remove it if so
    
    Args:
        path(str)
    """
    LOG.info("Removing file %s", path)
    try:
        os.remove(path)
        LOG.info("File %s removed", path)
    except OSError as err:
        LOG.info("File %s does not exists", path)
    return

def generate_hgnc(genes):
    """Generate lines from a file with reduced hgnc information
    
    Args:
        genes(dict): A dictionary with hgnc_id as key and hgnc_symbol as value
        outpath(str): Defaults to hgnc_reduced_path
    
    Yields:
        print_line(str): Lines from the reduced file
    """
    LOG.info("Generating new hgnc reduced file")
    # fetch the latest hgnc file here
    hgnc_gene_lines = fetch_hgnc() 

    header = None
    genes_found = 0
    
    # Loop over all hgnc gene lines
    for i,line in enumerate(hgnc_gene_lines):
        
        line = line.rstrip()
        # Skip lines that are empty
        if not len(line) > 0:
            continue
        # If we are reading the header, print it
        if i == 0:
            header = line.split('\t')
            yield line
            continue

        # Parse the hgnc gene line
        gene = parse_hgnc_line(line, header)
        if not gene:
            continue
        hgnc_id = int(gene['hgnc_id'])
        # Check if the gene is in the reduced
        if hgnc_id in genes:
            genes_found += 1
            yield line
    
    LOG.info("Number of genes printed to file: %s", genes_found)

def generate_genemap2(genes, api_key):
    """Generate a reduced file with omim genemap2 information
    
    Args:
        genes(dict): A dictionary with hgnc_symbol as key and hgnc_id as value
        api_key(str)

    Yields:
        print_line(str): Lines from the reduced file
    """
    
    mim_files = fetch_mim_files(api_key, genemap2=True)
    genemap2_lines = mim_files['genemap2']
    
    # Yield the header lines
    for line in genemap2_lines:
        if line.startswith('#'):
            yield line
        else:
            break
    
    for gene_info in parse_genemap2(genemap2_lines):
        hgnc_symbol = gene_info.get('hgnc_symbol')
        if not hgnc_symbol:
            continue
        if hgnc_symbol in genes:
            yield gene_info['raw']

def generate_mim2genes(genes, api_key):
    """Generate a reduced file with omim mim2gene information
    
    Args:
        genes(dict): A dictionary with hgnc_symbol as key and hgnc_id as value
        api_key(str)

    Yields:
        print_line(str): Lines from the reduced file
    """
    
    mim_files = fetch_mim_files(api_key, mim2genes=True)
    mim2gene_lines = mim_files['mim2genes']
    
    for line in mim2gene_lines:
        if line.startswith('#'):
            yield line
        else:
            break
    
    for gene_info in parse_mim2gene(mim2gene_lines):
        hgnc_symbol = gene_info.get('hgnc_symbol')
        if not hgnc_symbol:
            continue
        if hgnc_symbol in genes:
            yield gene_info['raw']

def generate_exac_genes(genes):
    """Generate a reduced file with omim mim2gene information
    
    Args:
        genes(dict): A dictionary with hgnc_symbol as key and hgnc_id as value
        outpath(str)

    Yields:
        print_line(str): Lines from the reduced file
    """
    exac_lines = fetch_exac_constraint()

    yield(exac_lines[0])
    
    for gene_info in parse_exac_genes(exac_lines):
        hgnc_symbol = gene_info.get('hgnc_symbol')
        if not hgnc_symbol:
            continue
        if hgnc_symbol in genes:
            yield gene_info['raw']

def generate_ensembl_genes(genes, silent=False, build=None):
    """Generate gene lines from a build

    Args:
        genes(dict): A dictionary with hgnc_id as key and hgnc_symbol as value
        silent(bool): If genes should be written to file or not
        build(str): What build to use. Defaults to 37
    
    Yields:
        print_line(str):  Lines from the reduced file
    """
    build = build or '37'

    ensembl_header = ['Chromosome/scaffold name', 'Gene start (bp)', 'Gene end (bp)',
                      'Gene stable ID', 'HGNC symbol', 'HGNC ID']

    yield '\t'.join(ensembl_header)
    
    ensembl_genes = fetch_ensembl_genes(build=build)

    nr_genes = 0

    # This function will yield dictionaries with ensemble info
    for gene_info in parse_ensembl_gene_request(ensembl_genes):
        hgnc_id = gene_info.get('hgnc_id')
        if not hgnc_id:
            continue
        if hgnc_id in genes:
            print_line = [
                gene_info['chrom'],
                str(gene_info['gene_start']),
                str(gene_info['gene_end']),
                gene_info['ensembl_gene_id'],
                gene_info['hgnc_symbol'],
                str(gene_info['hgnc_id']),
            ]
            yield '\t'.join(print_line)
            nr_genes += 1
    
    LOG.info("Nr genes collected for build %s: %s", build,nr_genes)

def generate_ensembl_transcripts(ensembl_genes, build):
    """Generate a file with reduced ensembl gene information
    
    Args:
        genes(dict): A dictionary with ensembl_id as key and hgnc_id as value
        silent(bool): If genes should be written to file or not
        build(str): What build to use. Defaults to 37
    
    Yields:
        print_line(str):  Lines from the reduced file
    
    """
    build = build or '37'
    
    ensembl_transcripts = fetch_ensembl_transcripts(build=build)
        
    ensembl_header = ['Chromosome/scaffold name', 'Gene stable ID', 
                   'Transcript stable ID', 'Transcript start (bp)', 
                   'Transcript end (bp)', 'RefSeq mRNA ID',
                   'RefSeq mRNA predicted ID', 'RefSeq ncRNA ID']
        
        
    yield '\t'.join(ensembl_header)
        
    for tx_info in parse_ensembl_transcript_request(ensembl_transcripts):
        ens_gene_id = tx_info['ensembl_gene_id']
        if ens_gene_id in ensembl_genes:
            print_line = [
                tx_info['chrom'],
                tx_info['ensembl_gene_id'],
                tx_info['ensembl_transcript_id'],
                str(tx_info['transcript_start']),
                str(tx_info['transcript_end']),
                tx_info['refseq_mrna'] or '',
                tx_info['refseq_mrna_predicted'] or '',
                tx_info['refseq_ncrna'] or '',
            ]
            yield '\t'.join(print_line)

def generate_hpo_genes(genes):
    """Generate the lines from a reduced hpo genes file
    
    Args:
        genes(dict): A map from hgnc_symbol to hgnc_id
    
    Yields:
        line(str): Lines from hpo with connection to genes
    """
    hpo_lines = fetch_hpo_genes()
    nr_terms = 0
    
    for i,line in enumerate(hpo_lines):
        line = line.rstrip()
        if not len(line) > 1:
            continue
        #Header line
        if i == 0:
            yield line
            continue

        splitted_line = line.split('\t')
        hgnc_symbol = splitted_line[1]
        
        if hgnc_symbol in genes:
            nr_terms
            yield line

def generate_hpo_terms(genes):
    """Generate the lines from a reduced hpo terms file
    
    Args:
        genes(dict): A map from hgnc_symbol to hgnc_id
    
    Yields:
        line(str): Lines from hpo with connection to genes
    """
    hpo_lines = fetch_hpo_genes()
    nr_terms = 0
    
    for i,line in enumerate(hpo_lines):
        line = line.rstrip()
        if not len(line) > 1:
            continue
        #Header line
        if i == 0:
            yield line
            continue

        splitted_line = line.split('\t')
        hgnc_symbol = splitted_line[1]
        
        if hgnc_symbol in genes:
            nr_terms
            yield line


def generate_hpo_files(genes):
    """Generate files with hpo reduced information"""
    hpo_files = fetch_hpo_files(hpogenes=True, hpoterms=True, phenotype_to_terms=True, hpodisease=False)
    
    file_names = {
        'hpogenes': hpogenes_reduced_path,
        'hpoterms': hpoterms_reduced_path,
        'phenotype_to_terms': hpo_phenotype_to_terms_reduced_path
    }
    
    for name in file_names:
        hpo_lines = hpo_files[name]
        out_path = file_names[name]
        outfile = open(out_path, 'w')
        LOG.info('Writing file %s', out_path)
        
        for i,line in enumerate(hpo_lines):
            line = line.rstrip()
            if not len(line) > 1:
                continue
            if i == 0:#Header line
                outfile.write(line+'\n')
                continue
            splitted_line = line.split('\t')
            if name == 'hpogenes':
                hgnc_symbol = splitted_line[1]
            elif name == 'hpoterms':
                hgnc_symbol = splitted_line[3]
            elif name == 'phenotype_to_terms':
                hgnc_symbol = splitted_line[1]
            
            if hgnc_symbol in genes:
                outfile.write(line+'\n')
        LOG.info("File ready")
