from scout.constants import CHR_PATTERN, PAR_COORDINATES


def is_par(chromosome, position, build="37"):
    """Check if a variant is in the Pseudo Autosomal Region or not

    Args:
        chromosome(str)
        position(int)
        build(str): The genome build

    Returns:
        bool
    """
    chrom_match = CHR_PATTERN.match(chromosome)
    chrom = chrom_match.group(2)

    # PAR regions are only on X and Y
    if not chrom in ["X", "Y"]:
        return False
    # Check if variant is in first PAR region
    if PAR_COORDINATES[build][chrom].at(position):
        return True

    return False
