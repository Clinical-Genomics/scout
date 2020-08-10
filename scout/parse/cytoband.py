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
        if line.startswith("#"):
            continue
        line = line.rstrip()
        splitted_line = line.split("\t")
        chrom = splitted_line[0].lstrip("chr")
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
