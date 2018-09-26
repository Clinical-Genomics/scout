
def add_links(gene_obj):
    """Update a gene object with links"""
    gene_obj['hgnc_link'] = genenames(gene_obj['hgnc_id'])
    gene_obj['omim_link'] = omim(gene_obj.get('hgnc_id'))
    
    ensembl_id = gene_obj['ensembl_id']
    gene_obj['ensembl_37_link'] = ensembl(ensembl_id, build=37)
    gene_obj['ensembl_38_link'] = ensembl(ensembl_id, build=38)
    gene_obj['omim_link'] = omim(gene_obj.get('hgnc_id'))

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
    build = int(build)

    link = ("http://grch37.ensembl.org/Homo_sapiens/Gene/Summary?"
                    "db=core;g={}")
    if build == 38:
        link = ("http://ensembl.org/Homo_sapiens/Gene/Summary?"
                        "db=core;g={}")
    if not ensembl_id:
        return None

    return link.format(ensembl_id)

def hpa(ensembl_id):
    link = "http://www.proteinatlas.org/search/{}"

    if not ensembl_id:
        return none

    return link.format(ensembl_id)

def string(ensembl_id):
    link = ("http://string-db.org/newstring_cgi/show_network_"
            "section.pl?identifier={}"

    if not ensembl_id:
        return none

    return link.format(ensembl_id)

def entrez(entrez_id):
    link = "https://www.ncbi.nlm.nih.gov/gene/{}"

    if not entrez_id:
        return none

    return link.format(entrez_id)

def ppaint(hgnc_symbol):
    link = "https://pecan.stjude.cloud/proteinpaint/{}"

    if not hgnc_symbol:
        return none

    return link.format(hgnc_symbol)
