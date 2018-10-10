from pprint import pprint as pp

def add_gene_links(gene_obj, build=37):
    """Update a gene object with links

    Args:
        gene_obj(dict)
        build(int)

    Returns:
        gene_obj(dict): gene_obj updated with many links
    """
    try:
        build = int(build)
    except ValueError:
        build = 37
    # Add links that use the hgnc_id
    hgnc_id = gene_obj['hgnc_id']

    gene_obj['hgnc_link'] = genenames(hgnc_id)
    gene_obj['omim_link'] = omim(hgnc_id)
    # Add links that use ensembl_id
    if not 'ensembl_id' in gene_obj:
        ensembl_id = gene_obj.get('common',{}).get('ensembl_id')
    else:
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
    gene_obj['exac_link'] = exac(ensembl_id)
    # Add links that use entrez_id
    gene_obj['entrez_link'] = entrez(gene_obj.get('entrez_id'))
    # Add links that use omim id
    gene_obj['omim_link'] = omim(gene_obj.get('omim_id'))
    # Add links that use hgnc_symbol
    gene_obj['ppaint_link'] = ppaint(gene_obj['hgnc_symbol'])
    # Add links that use vega_id
    gene_obj['vega_link'] = vega(gene_obj.get('vega_id'))
    # Add links that use ucsc link
    gene_obj['ucsc_link'] = ucsc(gene_obj.get('ucsc_id'))

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

def exac(ensembl_id):

    link = "http://exac.broadinstitute.org/gene/{}"
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

def vega(vega_id):
    link = "http://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?db=core;g=OTTHUMG00000018506{}"

    if not vega_id:
        return None

    return link.format(vega_id)

def ucsc(ucsc_id, build=37):
    link = "https://genome.ucsc.edu/cgi-bin/hgGene?db=hg{0}&hgg_chrom=chr10&hgg_gene={0}"

    if not ucsc_id:
        return None

    return link.format(build,ucsc_id)

def add_tx_links(tx_obj, build=37):
    try:
        build = int(build)
    except ValueError:
        build = 37

    ensembl_id = tx_obj.get('ensembl_transcript_id', tx_obj.get('transcript_id'))
    ensembl_37_link = ensembl_tx(ensembl_id, 37)
    ensembl_38_link = ensembl_tx(ensembl_id, 38)

    tx_obj['ensembl_37_link'] = ensembl_37_link
    tx_obj['ensembl_38_link'] = ensembl_38_link
    tx_obj['ensembl_link'] = ensembl_37_link
    if build == 38:
        tx_obj['ensembl_link'] = ensembl_38_link

    refseq_links = []
    if tx_obj.get('refseq_id'):
        refseq_id = tx_obj['refseq_id']
        refseq_links.append(
            {
                'link': refseq(refseq_id),
                'id': refseq_id
            }
        )
    tx_obj['refseq_links'] = refseq_links
    tx_obj['swiss_prot_link'] = swiss_prot(tx_obj.get('swiss_prot'))
    tx_obj['pfam_domain_link'] = pfam(tx_obj.get('pfam_domain'))
    tx_obj['prosite_profile_link'] = prosite(tx_obj.get('prosite_profile'))
    tx_obj['smart_domain_link'] = smart(tx_obj.get('smart_domain'))

    return tx_obj


##  Transcript links
def refseq(refseq_id):
    link = "http://www.ncbi.nlm.nih.gov/nuccore/{}"
    if not refseq_id:
        return None

    return link.format(refseq_id)

def ensembl_tx(ens_tx_id, build=37):
    link = ("http://grch37.ensembl.org/Homo_sapiens/"
                    "Gene/Summary?t={}")

    if build == 38:
        link = ("http://ensembl.org/Homo_sapiens/"
                        "Gene/Summary?t={}")
    if not ens_tx_id:
        return None

    return link.format(ens_tx_id)

def swiss_prot(swiss_prot_id):
    link = "http://www.uniprot.org/uniprot/{}"

    if not swiss_prot_id:
        return None

    return link.format(swiss_prot_id)

def pfam(pfam_domain):
    link = "http://pfam.xfam.org/family/{}"

    if not pfam_domain:
        return None

    return link.format(pfam_domain)

def prosite(prosat_profile):
    link = ("http://prosite.expasy.org/cgi-bin/prosite/"
                                      "prosite-search-ac?{}")
    if not prosat_profile:
        return None

    return link.format(prosat_profile)

def smart(smart_domain):
    link = "http://smart.embl.de/smart/search.cgi?keywords={}"

    if not smart_domain:
        return None

    return link.format(smart_domain)
