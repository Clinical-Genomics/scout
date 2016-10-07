from codecs import open

def parse_genes(panel_path, panel_name):
    """Parse a file with genes and return the hgnc ids
    
        Args:
            panel_path(str): Path to gene panel file
            panel_name(str): Name of the gene panel
        
        Returns:
            genes(list(str)): List of hgnc ids
    """
    genes = []
    header = []
    
    with open(panel_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('#'):
                if not line.startswith('##'):
                    header = line[1:].split('\t')
            else:
                line = line.split('\t')
                gene_info = dict(zip(header, line))
                #These are the panels that the gene belongs to:
                gene_panels = set(gene_info.get('Clinical_db_gene_annotation','').split(','))
                hgnc_symbols = gene_info.get('HGNC_symbol','').split(',')
                chromosome = gene_info.get('Chromosome')
                start = int(gene_info.get('Gene_start', '0'))
                stop = int(gene_info.get('Gene_stop', '0'))
                ensembl_gene_id = gene_info.get('Ensembl_gene_id')
                description = gene_info.get('Gene_description')
                locus = gene_info.get('Gene_locus')
                # mim_id = gene_info.get('Gene_stop', '0')
                # if mim_id:
                #     mim_id = int(mim_id)
                protein_name = gene_info.get('Protein_name')
                reduced_penetrance = gene_info.get('Reduced_penetrance')
                if reduced_penetrance:
                    reduced_penetrance = True
                else:
                    reduced_penetrance = False

                if panel_name in gene_panels:
                    for hgnc_symbol in hgnc_symbols:
                        genes.append(hgnc_symbol)

    return genes

def parse_gene_panel(panel_info):
    """Parse the panel info and return a gene panel
        
        Args:
            panel_info(dict)
    
        Returns:
            gene_panel(dict)
    """
    
    gene_panel = {}
    
    gene_panel['path'] = panel_info.get('file')
    gene_panel['type'] = panel_info.get('type', 'clinical')
    gene_panel['date'] = panel_info.get('date')
    gene_panel['version'] = float(panel_info.get('version', '0'))
    gene_panel['id'] = panel_info.get('name')
    gene_panel['display_name'] = panel_info.get('full_name', gene_panel['id'])
    
    gene_panel['genes'] = parse_genes(
        panel_path = gene_panel['path'],
        panel_name = gene_panel['id']
    )
    
    return gene_panel
    
    