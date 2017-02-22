import click

from scout.utils.handle import get_file_handle

def get_hgnc_genes(lines):
    """Return a set with hgnc symbols"""
    hgnc_symbols = set()
    for index, line in enumerate(lines):
        if index > 0:
            line = line.rstrip().split('\t')
            hgnc_symbols.add(line[1])
    return hgnc_symbols

def print_mim2gene(mim2gene_lines, hgnc_symbols):
    """docstring for print_mim2gene"""
    for line in mim2gene_lines:
        line = line.rstrip()
        if line.startswith('#'):
            print(line)
        else:
            splitted_line = line.split('\t')
            if len(splitted_line) > 3:
                hgnc_symbol = splitted_line[3]
                if hgnc_symbol in hgnc_symbols:
                    print(line)

def print_genemap(genemap_lines, hgnc_symbols):
    """docstring for print_genemap"""
    for line in genemap_lines:
        line = line.rstrip()
        if line.startswith('#'):
            print(line)
        else:
            splitted_line = line.split('\t')
            if len(splitted_line) > 8:
                hgnc_symbol = splitted_line[8]
                if hgnc_symbol:
                    if hgnc_symbol in hgnc_symbols:
                        print(line)
        

@click.command()
@click.option('--hgnc', type=click.Path(exists=True))
@click.option('--mim2gene', type=click.Path(exists=True))
@click.option('--genemap', type=click.Path(exists=True))
@click.pass_context
def mim(ctx, hgnc, mim2gene, genemap):
    """docstring for mim"""
    if not hgnc:
        click.echo("Please provide the hgnc gene file")
        ctx.abort()
        
    hgnc_handle = get_file_handle(hgnc)
    hgnc_genes = get_hgnc_genes(hgnc_handle)
    
    if mim2gene:
        mim2gene_handle = get_file_handle(mim2gene)
        print_mim2gene(mim2gene_handle, hgnc_genes)
    elif genemap:
        genemap_handle = get_file_handle(genemap)
        print_genemap(genemap_handle, hgnc_genes)
    else:
        click.echo("Please provide either mim2gene or genemap file")
        ctx.abort()
        
    
    


if __name__ == '__main__':
    mim()