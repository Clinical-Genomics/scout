import logging
import intervaltree


def parse_cytoband(lines):
    """Parse iterable with cytoband coordinates
    
    
    Args:
        lines(iterable): Strings on format "chr1\t2300000\t5400000\tp36.32\tgpos25"
    
    Returns:
        cytobands(dict): Dictionary with chromosome names as keys and 
                         interval trees as values
    """
    cytobands = {}
    for line in lines:
        line = line.rstrip()
        splitted_line = line.split('\t')
        chrom = splitted_line[0].lstrip('chr')
        start = int(splitted_line[1])
        stop = int(splitted_line[2])
        name = splitted_line[3]
        if chrom in cytobands:
            # Add interval to existing tree
            cytobands[chrom][start:stop] = name
        else:
            # Create a new interval tree
            new_tree = intervaltree.IntervalTree()
            # create the interval
            new_tree[start:stop] = name
            # Add the interval tree 
            cytobands[chrom] = new_tree
    
    return cytobands 


import click
from scout.utils.handle import get_file_handle
from scout.resources import cytobands_path

@click.command()
@click.option('--infile', default=cytobands_path)
def cli(infile):
    """docstring for cli"""
    lines = get_file_handle(infile)
    cytobands = parse_cytoband(lines)
    
    print("Check some coordinates:")
    
    print("checking chrom 1 pos 2")
    intervals = cytobands['1'][2]
    for interval in intervals:
        print(interval)
        print(interval.begin)
        print(interval.end)
        print(interval.data)
        # print(interval.__dict__)
    print(cytobands['1'][2])
    
    print("checking chrom 8 pos 101677777")
    print(cytobands['8'][101677777])

    print("checking chrom X pos 4200000 - 6000000")
    print(cytobands['X'][4200000:6000000])


if __name__ == '__main__':
    cli()