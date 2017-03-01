import sys
import re
import click
import logging
from pprint import pprint as pp

mimnr_pattern = re.compile("[0-9]{6,6}")

mim_inheritance_terms = [
        'Autosomal recessive',
        'Autosomal dominant',
        'X-linked dominant',
        'X-linked recessive',
        'Y-linked',
        'Mitochondrial'
    ]

TERMS_MAPPER = {
     'Autosomal recessive': 'AR',
     'Autosomal dominant': 'AD',
     'X-linked dominant': 'XD',
     'X-linked recessive': 'XR',
     'Y-linked': 'Y',
     'Mitochondrial': 'MT'
   }

log = logging.getLogger(__name__)

def parse_omim_line(line, header):
    """docstring for parse_omim_2_line"""
    omim_info = dict(zip(header, line.split('\t')))
    return omim_info

def parse_genemap2(lines):
    """Parse the omim source file called genemap2.txt
    
    Explanation of Phenotype field:
    Brackets, "[ ]", indicate "nondiseases," mainly genetic variations that 
    lead to apparently abnormal laboratory test values.

    Braces, "{ }", indicate mutations that contribute to susceptibility to 
    multifactorial disorders (e.g., diabetes, asthma) or to susceptibility 
    to infection (e.g., malaria).

    A question mark, "?", before the phenotype name indicates that the 
    relationship between the phenotype and gene is provisional. 
    More details about this relationship are provided in the comment 
    field of the map and in the gene and phenotype OMIM entries.

    The number in parentheses after the name of each disorder indicates 
    the following: 
        (1) the disorder was positioned by mapping of the wildtype gene; 
        (2) the disease phenotype itself was mapped; 
        (3) the molecular basis of the disorder is known; 
        (4) the disorder is a chromosome deletion or duplication syndrome. 
    
    Args:
        lines(iterable(str))
    
    Yields:
        parsed_entry(dict)
    """
    log.info("Parsing the omim genemap2")
    header = []
    for i,line in enumerate(lines):
        line = line.rstrip()
        if line.startswith('#'):
            if i < 10:
                if line.startswith('# Chromosome'):
                    header = line[2:].split('\t')
        else:
            parsed_entry = parse_omim_line(line, header)
            parsed_entry['mim_number'] = int(parsed_entry['Mim Number'])
            hgnc_symbol = parsed_entry.get("Approved Symbol")
            if not hgnc_symbol:
                if parsed_entry.get('Gene Symbols'):
                    hgnc_symbol = parsed_entry['Gene Symbols'].split(',')[0].strip() 
            parsed_entry['hgnc_symbol'] = hgnc_symbol
            gene_inheritance = set()
            parsed_phenotypes = []
            # These information about the related phenotypes
            if parsed_entry.get('Phenotypes'):
                # Each related phenotype is separated by ';'
                for phenotype_info in parsed_entry['Phenotypes'].split(';'):
                    inheritance = set()
                    match = mimnr_pattern.search(phenotype_info)
                    if match:
                        phenotype_mim = int(match.group())
                        for term in mim_inheritance_terms:
                            if term in phenotype_info:
                                inheritance.add(TERMS_MAPPER[term])
                                gene_inheritance.add(TERMS_MAPPER[term])
                        parsed_phenotypes.append(
                            {
                                'mim_number':phenotype_mim, 
                                'inheritance': inheritance
                            }
                        )
            parsed_entry['phenotypes'] = parsed_phenotypes
            parsed_entry['inheritance'] = gene_inheritance
                    
            yield parsed_entry


def parse_mim2gene(lines):
    """Parse the file called mim2gene
    
    This file describes what typ the different mim numbers have.
    The different entry types are: 'gene', 'gene/phenotype', 'moved/removed',
    'phenotype', 'predominantly phenotypes'
    Where:
        gene: Is a gene entry
        gene/phenotype: This entry describes both a phenotype and a gene
        moved/removed: No explanation needed
        phenotype: Describes a phenotype
        predominantly phenotype: Not clearly established
    
    Args:
        lines(iterable(str)): The mim2gene lines
    
    Yields:
        dict
    
    """
    log.info("Parsing mim2gene")
    header = ["mim_number", "entry_type", "entrez_gene_id", "hgnc_symbol", "ensembl_gene_id"]
    for i, line in enumerate(lines):
        line = line.rstrip()
        if not line.startswith('#'):
            parsed_entry = parse_omim_line(line, header)
            parsed_entry['mim_number'] = int(parsed_entry['mim_number'])
            if 'hgnc_symbol' in parsed_entry:
                parsed_entry['hgnc_symbol'] = parsed_entry['hgnc_symbol'].upper()
            yield parsed_entry

def parse_omim_morbid(lines):
    """docstring for parse_omim_morbid"""
    header = []
    for i,line in enumerate(lines):
        line = line.rstrip()
        if line.startswith('#'):
            if i < 10:
                if line.startswith('# Phenotype'):
                    header = line[2:].split('\t')
        else:
            yield parse_omim_line(line, header)

def parse_mim_titles(lines):
    """docstring for parse_omim_morbid"""
    header = ['prefix', 'mim_number', 'preferred_title', 'alternative_title', 'included_title']
    for i,line in enumerate(lines):
        line = line.rstrip()
        if not line.startswith('#'):
            parsed_entry = parse_omim_line(line, header)
            parsed_entry['mim_number'] = int(parsed_entry['mim_number'])
            parsed_entry['preferred_title'] = parsed_entry['preferred_title'].split(';')[0]
            yield parsed_entry

def get_mim_genes(genemap_lines, mim2gene_lines):
    """Get a dictionary with genes and their omim information
    
    Args:
        genemap_lines(iterable(str))
        mim2gene_lines(iterable(str))
    
    Returns.
        hgnc_genes(dict): A dictionary with hgnc_symbol as keys
    
    """
    log.info("Get the mim genes")
    
    genes = {}
    hgnc_genes = {}
    
    gene_nr = 0
    no_hgnc = 0
    
    for entry in parse_mim2gene(mim2gene_lines):
        if 'gene' in entry['entry_type']:
            mim_nr = entry['mim_number']
            gene_nr += 1
            if not 'hgnc_symbol' in entry:
                no_hgnc += 1
            else:
                genes[mim_nr] = entry
    
    for entry in parse_genemap2(genemap_lines):
        mim_number = entry['mim_number']
        inheritance = entry['inheritance']
        phenotype_info = entry['phenotypes']
        hgnc_symbol = entry['hgnc_symbol']
        if mim_number in genes:
            genes[mim_number]['inheritance'] = inheritance

    for mim_nr in genes:
        gene_info = genes[mim_nr]
        hgnc_genes[gene_info['hgnc_symbol']] = gene_info
    
    return hgnc_genes
    
def get_mim_phenotypes(genemap_lines, mim2gene_lines, mimtitles_lines):
    """Get a dictionary with phenotypes
    
    Use the mim numbers for phenitypes as keys and phenotype information as 
    values.
    
    Args:
        genemap_lines(iterable(str))
        mim2gene_lines(iterable(str))
        mimtitles_lines(iterable(str))
    
    Returns:
        phenotypes_found(dict): A dictionary with mim_numbers as keys and 
        dictionaries with phenotype information as values.
    
        {
            'description': str, # Description of the phenotype
             'hgnc_symbols': set(), # Associated hgnc symbols
             'inheritance': set(),  # Associated phenotypes
             'mim_number': int, # mim number of phenotype
        }
    """
    # Set with all omim numbers that are phenotypes
    # Parsed from mim2gene.txt
    phenotype_mims = set()
    
    phenotypes_found = {}
    
    for entry in parse_mim2gene(mim2gene_lines):
        if 'phenotype' in entry['entry_type']:
            phenotype_mims.add(entry['mim_number'])

    for entry in parse_mim_titles(mimtitles_lines):
        mim_number = entry['mim_number']
        if mim_number in phenotype_mims:
            phenotype_entry = {
                'mim_number': mim_number,
                'description': entry['preferred_title'],
                'hgnc_symbols': set(),
                'inheritance': set()
            }
            phenotypes_found[mim_number] = phenotype_entry

    for entry in parse_genemap2(genemap_lines):
        hgnc_symbol = entry['hgnc_symbol']
        for phenotype in entry['phenotypes']:
            mim_nr = phenotype['mim_number']
            if mim_nr in phenotypes_found:
                phenotype_entry = phenotypes_found[mim_nr]
                phenotype_entry['inheritance'] = phenotype_entry['inheritance'].union(phenotype['inheritance'])
                phenotype_entry['hgnc_symbols'].add(hgnc_symbol)

    return phenotypes_found
    

@click.command()
@click.option('--morbid', type=click.Path(exists=True))
@click.option('--genemap', type=click.Path(exists=True))
@click.option('--mim2gene', type=click.Path(exists=True))
@click.option('--mim_titles', type=click.Path(exists=True))
@click.pass_context
def cli(context, morbid, genemap, mim2gene, mim_titles):
    """Parse the omim files"""
    if not (morbid and genemap and mim2gene, mim_titles):
        print("Please provide all files")
        context.abort()

    from scout.utils.handle import get_file_handle
    
    print("Morbid file: %s" % morbid)
    print("Genemap file: %s" % genemap)
    print("mim2gene file: %s" % mim2gene)
    print("MimTitles file: %s" % mim_titles)

    morbid_handle = get_file_handle(morbid)
    genemap_handle = get_file_handle(genemap)
    mim2gene_handle = get_file_handle(mim2gene)
    mimtitles_handle = get_file_handle(mim_titles)
    
    # hgnc_genes = get_mim_genes(genemap_handle, mim2gene_handle)
    # for hgnc_symbol in hgnc_genes:
    #     pp(hgnc_genes[hgnc_symbol])
    # phenotypes = get_mim_phenotypes(genemap_handle, mim2gene_handle, mimtitles_handle)
    # for mim_nr in phenotypes:
    #     pp(phenotypes[mim_nr])
    
    genes = get_mim_genes(genemap_handle, mim2gene_handle)
    for hgnc_symbol in genes:
        pp(genes[hgnc_symbol])
    
    # genes = {}
    # phenotypes = {}
    # no_hgnc = 0
    # gene_nr = 0
    # predominantly = 0
    # moved = 0
    # phenotype_nr = 0
    # for entry in parse_mim2gene(mim2gene_handle):
    #     mim_nr = entry['mim_number']
    #     # pp(entry)
    #     if entry['entry_type'] == 'predominantly phenotypes':
    #         predominantly += 1
    #         continue
    #     if entry['entry_type'] == 'moved/removed':
    #         moved += 1
    #         continue
    #     if 'gene' in entry['entry_type']:
    #         gene_nr += 1
    #         if not 'hgnc_symbol' in entry:
    #             no_hgnc += 1
    #         else:
    #             genes[mim_nr] = entry
    #     if 'phenotype' in entry['entry_type']:
    #         phenotype_nr += 1
    #         entry['genes'] = set()
    #         entry['inheritance'] = set()
    #         phenotypes[mim_nr] = entry
    #
    # click.echo("Number of genes: %s" % gene_nr)
    # click.echo("Number of genes without hgnc: %s" % no_hgnc)
    # click.echo("Number of phenotypes: %s" % phenotype_nr)
    # click.echo("Predominantly phenotypes: %s" % predominantly)
    # click.echo("Number of moved: %s" % moved)
    #
    # for entry in parse_mim_titles(mimtitles_handle):
    #     if entry['prefix'] not in ['NULL', 'Caret']:
    #         mim_nr = entry['mim_number']
    #         if mim_nr in genes:
    #             genes[mim_nr]['description'] = entry['preferred_title']
    #         if mim_nr in phenotypes:
    #             phenotypes[mim_nr]['description'] = entry['preferred_title']
    #
    # # print('')
    #
    # for entry in parse_genemap2(genemap_handle):
    #     mim_number = entry['mim_number']
    #     inheritance = entry['inheritance']
    #     phenotype_info = entry['phenotypes']
    #     hgnc_symbol = entry['hgnc_symbol']
    #     if mim_number in genes:
    #         genes[mim_number]['inheritance'] = inheritance
    #     for phenotype in phenotype_info:
    #         phenotype_mim = phenotype['mim_number']
    #         if phenotype_mim in phenotypes:
    #             phenotypes[phenotype_mim]['inheritance'] = phenotypes[phenotype_mim]['inheritance'].union(phenotype['inheritance'])
    #             phenotypes[phenotype_mim]['genes'].add(hgnc_symbol)
    #
    #     #
    #     #     pp(entry)
    # # for mim_nr in genes:
    # #     pp(genes[mim_nr])
    # for mim_nr in phenotypes:
    #     if phenotypes[mim_nr]['entry_type'] == 'predominantly phenotypes':
    #         pp(phenotypes[mim_nr])


if __name__ == '__main__':
    cli()