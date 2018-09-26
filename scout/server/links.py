
def add_gene_links(gene_obj, build=37):
    """Update a gene object with links

    Args:
        gene_obj(dict)
        build(int)

    Returns:
        gene_obj(dict): gene_obj updated with many links
    """
    build = int(build)

    # Add links that use the hgnc_id
    hgnc_id = gene_obj['hgnc_id']
    gene_obj['hgnc_link'] = genenames(hgnc_id)
    gene_obj['omim_link'] = omim(hgnc_id)
    # Add links that use ensembl_id
    ensembl_id = gene_obj['ensembl_id']
    ensembl_37_link = ensembl(ensembl_id, build=37)
    ensembl_38_link = ensembl(ensembl_id, build=38)
    gene_obj['ensembl_37_link'] = ensembl_37_link
    gene_obj['ensembl_38_link'] = ensembl_38_link
    gene_obj['ensembl_link'] = ensembl_37_link
    if build == 38:
        gene_obj['ensembl_link'] = ensembl_38_link
    gene_obj['hpa_link'] = hpa(ensembl_id)
    gene_obj['string_link'] = string(ensembl_id)
    gene_obj['reactome_link'] = reactome(ensembl_id)
    gene_obj['expression_atlas_link'] = expression_atlas(ensembl_id)
    # Add links that use entrez_id
    gene_obj['entrez_link'] = entrez(gene_obj.get('entrez_id'))
    # Add links that use omim id
    gene_obj['omim_link'] = omim(gene_obj.get('omim_id'))
    # Add links that use hgnc_symbol
    gene_obj['ppaint_link'] = ppaint(gene_obj['hgnc_symbol'])

def genenames(hgnc_id):
    link = "https://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id=HGNC:{}"
    if not hgnc_id:
        return None
    return link.format(hgnc_id)

def omim(omim_id):
    link = "https://www.omim.org/entry/{}"
    if not omim_id:
        return None
    return link.format(omim_id)

def ensembl(ensembl_id, build=37):

    link = "http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={}"
    if build == 38:
        link = "http://ensembl.org/Homo_sapiens/Gene/Summary?db=core;g={}"
    if not ensembl_id:
        return None

    return link.format(ensembl_id)

def hpa(ensembl_id):
    link = "http://www.proteinatlas.org/search/{}"

    if not ensembl_id:
        return None

    return link.format(ensembl_id)

def string(ensembl_id):
    link = ("http://string-db.org/newstring_cgi/show_network_"
            "section.pl?identifier={}")

    if not ensembl_id:
        return None

    return link.format(ensembl_id)

def reactome(ensembl_id):
    link = ("http://www.reactome.org/content/query?q={}&species=Homo+sapiens"
            "&species=Entries+without+species&cluster=true")
    if not ensembl_id:
        return None

    return link.format(ensembl_id)

def expression_atlas(ensembl_id):
    link = "https://www.ebi.ac.uk/gxa/genes/{}"
    if not ensembl_id:
        return None

    return link.format(ensembl_id)

def entrez(entrez_id):
    link = "https://www.ncbi.nlm.nih.gov/gene/{}"

    if not entrez_id:
        return None

    return link.format(entrez_id)

def ppaint(hgnc_symbol):
    link = "https://pecan.stjude.cloud/proteinpaint/{}"

    if not hgnc_symbol:
        return None

    return link.format(hgnc_symbol)
