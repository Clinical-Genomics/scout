import os
import logging

from pprint import pprint as pp

from scout.utils.requests import (fetch_hgnc, fetch_mim_files, fetch_exac_constraint, 
fetch_ensembl_genes, fetch_ensembl_transcripts, fetch_hpo_files)
from scout.parse.hgnc import parse_hgnc_line
from scout.parse.omim import parse_genemap2, parse_mim2gene
from scout.parse.exac import parse_exac_genes
from scout.parse.ensembl import (parse_ensembl_gene_request, parse_ensembl_transcript_request)

from . import (hgnc_reduced_path, genemap2_reduced_path, mim2gene_reduced_path, exac_reduced_path, 
genes37_reduced_path, genes38_reduced_path, transcripts37_reduced_path, transcripts38_reduced_path,
hpogenes_reduced_path, hpoterms_reduced_path, hpo_phenotype_to_terms_reduced_path)

LOG = logging.getLogger(__name__)

def remove_file(path):
    """Check if a file exists and remove it if so
    
    Args:
        path(str)
    """
    try:
        os.remove(path)
        LOG.info("File %s removed", path)
    except OSError as err:
        LOG.info("File %s does not exists", path)
    return

def generate_hgnc(panel_genes, outpath=hgnc_reduced_path):
    """Generate a reduced file with hgnc information
    
    Args:
        panel_genes(dict): A dictionary with hgnc_id as key and hgnc_symbol as value
        outpath(str): Defaults to hgnc_reduced_path
    """
    
    hgnc_gene_lines = fetch_hgnc() # fetch the latest hgnc file here
    
    remove_file(outpath)
    
    outfile = open(outpath, 'w')
    
    header = None
    for i,line in enumerate(hgnc_gene_lines):
        line = line.rstrip()
        if not len(line) > 0:
            continue
        if i == 0:
            outfile.write(line+'\n')
            header = line.split('\t')
            LOG.debug("writing header to hgnc file")
            continue
        gene = parse_hgnc_line(line, header)
        if not gene:
            continue
        hgnc_id = gene['hgnc_id']
        if hgnc_id in panel_genes:
            LOG.debug("writing gene %s to hgnc file", hgnc_id)
            outfile.write(line+'\n')

def generate_genemap2(panel_genes, api_key, outpath=genemap2_reduced_path):
    """Generate a reduced file with omim genemap2 information
    
    Args:
        panel_genes(dict): A dictionary with hgnc_symbol as key and hgnc_id as value
        api_key(str)
        outpath(str)
    """
    
    mim_files = fetch_mim_files(api_key, genemap2=True)
    genemap2_lines = mim_files['genemap2']
    
    remove_file(outpath)
    
    outfile = open(outpath, 'w')
    for line in genemap2_lines:
        if line.startswith('#'):
            outfile.write(line + '\n')
        else:
            break
    
    for gene_info in parse_genemap2(genemap2_lines):
        hgnc_symbol = gene_info.get('hgnc_symbol')
        if not hgnc_symbol:
            continue
        if hgnc_symbol in panel_genes:
            outfile.write(gene_info['raw'] + '\n')

def generate_mim2genes(panel_genes, api_key, outpath=mim2gene_reduced_path):
    """Generate a reduced file with omim mim2gene information
    
    Args:
        panel_genes(dict): A dictionary with hgnc_symbol as key and hgnc_id as value
        api_key(str)
        outpath(str)
    """
    
    mim_files = fetch_mim_files(api_key, mim2genes=True)
    mim2gene_lines = mim_files['mim2genes']
    
    remove_file(outpath)
    
    outfile = open(outpath, 'w')
    for line in mim2gene_lines:
        if line.startswith('#'):
            outfile.write(line + '\n')
        else:
            break
    
    for gene_info in parse_mim2gene(mim2gene_lines):
        hgnc_symbol = gene_info.get('hgnc_symbol')
        if not hgnc_symbol:
            continue
        if hgnc_symbol in panel_genes:
            outfile.write(gene_info['raw'] + '\n')

def generate_exac_genes(panel_genes, outpath=exac_reduced_path):
    """Generate a reduced file with omim mim2gene information
    
    Args:
        panel_genes(dict): A dictionary with hgnc_symbol as key and hgnc_id as value
        outpath(str)
    """
    exac_lines = fetch_exac_constraint()
    
    remove_file(outpath)
    
    outfile = open(outpath, 'w')
    outfile.write(exac_lines[0] + '\n')
    
    for gene_info in parse_exac_genes(exac_lines):
        hgnc_symbol = gene_info.get('hgnc_symbol')
        if not hgnc_symbol:
            continue
        if hgnc_symbol in panel_genes:
            outfile.write(gene_info['raw'] + '\n')

def generate_ensembl_genes(panel_genes):
    """Generate a file with reduced ensembl gene information"""
    builds = ['37', '38']
    outpaths = [genes37_reduced_path, genes38_reduced_path]
    
    ensembl_genes = {'37':set(), '38':set()}
    
    for i, build in enumerate(builds):
        outpath = outpaths[i]
        ensembl_genes = fetch_ensembl_genes(build=build)
        
        ensembl_header = ['Chromosome/scaffold name', 'Gene start (bp)', 'Gene end (bp)',
                          'Gene stable ID', 'HGNC symbol', 'HGNC ID']
        
        remove_file(outpath)
        
        outfile = open(outpath, 'w')
        outfile.write('\t'.join(ensembl_header) + '\n')
        
        for gene_info in parse_ensembl_gene_request(ensembl_genes):
            hgnc_id = gene_info.get('hgnc_id')
            if not hgnc_id:
                continue
            if hgnc_id in panel_genes:
                print_line = [
                    gene_info['chrom'],
                    str(gene_info['gene_start']),
                    str(gene_info['gene_end']),
                    gene_info['ensembl_gene_id'],
                    gene_info['hgnc_symbol'],
                    str(gene_info['hgnc_id']),
                ]
                outfile.write('\t'.join(print_line) + '\n')
                
                ensembl_genes[build].add(gene_info['ensembl_gene_id'])
    return ensembl_genes

def generate_ensembl_transcripts(ensembl_genes):
    """Generate a file with reduced ensembl gene information"""
    builds = ['37', '38']
    outpaths = [transcripts37_reduced_path, transcripts38_reduced_path]
    
    for i, build in enumerate(builds):
        genes = ensembl_genes[build]
        outpath = outpaths[i]
        ensembl_transcripts = fetch_ensembl_transcripts(build=build)
        
        ensembl_header = ['Chromosome/scaffold name', 'Gene stable ID', 
                   'Transcript stable ID', 'Transcript start (bp)', 
                   'Transcript end (bp)', 'RefSeq mRNA ID',
                   'RefSeq mRNA predicted ID', 'RefSeq ncRNA ID']
        
        remove_file(outpath)
        
        outfile = open(outpath, 'w')
        outfile.write('\t'.join(ensembl_header) + '\n')
        
        for tx_info in parse_ensembl_transcript_request(ensembl_transcripts):
            ens_gene_id = tx_info['ensembl_gene_id']
            if ens_gene_id in genes:
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
                outfile.write('\t'.join(print_line) + '\n')

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
