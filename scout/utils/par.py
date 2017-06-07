from scout.constants import PAR_COORDINATES

def is_par(chromosome, position, build='37'):
    """Check if a variant is in the Pseudo Autosomal Region or not
    
    Args:
        chromosome(str)
        position(int)
        build(str): The genome build
    
    Returns:
        bool
    """
    if chromosome in ['X','Y']:
        # Check if variant is in first PAR region
        res = PAR_COORDINATES[build][chromosome].search(position)
        if res:
            return True
    
    return False