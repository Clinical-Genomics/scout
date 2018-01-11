import logging
import click
import urllib.request

from pprint import pprint as pp

from scout.parse.omim import (parse_genemap2, parse_mim2gene, parse_omim_morbid, parse_mim_titles,
                              get_mim_genes, get_mim_phenotypes)

LOG = logging.getLogger(__name__)

API_KEY = 'Sm30VutuQlmvAKzCtnnV_g'

@click.command('omim', short_help='Update omim gene panel')
@click.pass_context
def omim(context):
    """
    Update the automate omim gene panel in the database
    """
    adapter = context.obj['adapter']
    
    mim2genes_url = 'https://omim.org/static/omim/data/mim2gene.txt'
    mimtitles_url = 'https://data.omim.org/downloads/{0}/mimTitles.txt'.format(API_KEY)
    genemap_url = 'https://data.omim.org/downloads/{0}/genemap.txt'.format(API_KEY)
    morbidmap_url = 'https://data.omim.org/downloads/{0}/morbidmap.txt'.format(API_KEY)
    genemap2_url = 'https://data.omim.org/downloads/{0}/genemap2.txt'.format(API_KEY)
    
    ############# genemap2 ##############
    
    # response = urllib.request.urlopen(genemap2_url)
    # data = response.read()      # a `bytes` object
    # text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    #
    # for i, line in enumerate(text.split('\n')):
    #     if i > 10:
    #         print('\n\n')
    #         break
    #     print(line)

    # genemap2_parsed = parse_genemap2(text.split('\n'))
    # for i, line in genemap2_parsed:
    #     if i > 10:
    #         break
    #     if len(line) > 0:
    #         print(line)

    ############# mim2genes ##############

    # response = urllib.request.urlopen(mim2genes_url)
    # data = response.read()      # a `bytes` object
    # text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    #
    # for i, line in enumerate(text.split('\n')):
    #     if i > 10:
    #         print('\n\n')
    #         break
    #     print(line)
    
    # for line in text.split('\n'):
    #     print(line)
    
    # mim2genes_parsed = parse_mim2gene(text.split('\n'))
    # for line in mim2genes_parsed:
    #     if len(line) > 0:
    #         pp(line)

    ############# morbidmap ##############

    # response = urllib.request.urlopen(morbidmap_url)
    # data = response.read()      # a `bytes` object
    # text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    #
    # for i, line in enumerate(text.split('\n')):
    #     if i > 10:
    #         print('\n\n')
    #         break
    #     print(line)
    
    # for line in text.split('\n'):
    #     print(line)
    
    # morbid_parsed = parse_omim_morbid(text.split('\n'))
    # for line in morbid_parsed:
    #     if len(line) > 0:
    #         pp(line)

    ############# mimtitles ##############

    # response = urllib.request.urlopen(mimtitles_url)
    # data = response.read()      # a `bytes` object
    # text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    #
    # for i, line in enumerate(text.split('\n')):
    #     if i > 10:
    #         print('\n\n')
    #         break
    #     print(line)
    
    # for line in text.split('\n'):
    #     print(line)
    
    # mimtitles_parsed = parse_mim_titles(text.split('\n'))
    # for line in mimtitles_parsed:
    #     if len(line) > 0:
    #         pp(line)
    
    ############# mimgenes ##############

    genemap_response = urllib.request.urlopen(genemap2_url)
    mim2gene_response = urllib.request.urlopen(mim2genes_url)
    
    genemap_data = genemap_response.read() # a `bytes` object
    genemap_text = genemap_data.decode('utf-8').split('\n')

    mim2gene_data = mim2gene_response.read() # a `bytes` object
    mim2gene_text = mim2gene_data.decode('utf-8').split('\n')
    
    # for line in mim2gene_text:
    #     print(line)
    
    # for gene in parse_mim2gene(mim2gene_text):
    #     print(gene)
    
    STATUS_TO_ADD = set(['established', 'provisional'])
    
    parsed_genes = get_mim_genes(genemap_text, mim2gene_text)
    for hgnc_symbol in parsed_genes:
        try:
            gene = parsed_genes[hgnc_symbol]
            keep = False
            for phenotype_info in gene.get('phenotypes',[]):
                if phenotype_info['status'] in STATUS_TO_ADD:
                    keep = True
                    break
            if keep:
                print(gene['hgnc_symbol'])
        except KeyError:
            pp(gene)
        # pp(parsed_genes[gene])

    
    # parsed_phenotypes = get_mim_phenotypes(genemap_text)
    # for phenotype in parsed_phenotypes:
    #     pp(parsed_phenotypes[phenotype])
    #