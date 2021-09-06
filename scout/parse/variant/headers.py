"""
Functions to parse information from vcf headers
"""


def parse_rank_results_header(vcf_obj):
    """Return a list with the rank results header

    Check if the rank result is in the vcf header. If it exists return a list
    with the rank results headers

    Args:
        vcf_obj(cyvcf2.VCF)

    Returns:
        rank_results_header(list)
    """
    rank_results_header = []

    if "RankResult" in vcf_obj:
        rank_results_header = vcf_obj["RankResult"]["Description"].strip('"').split("|")

    return rank_results_header


def parse_header_format(description):
    """Get the format from a vcf header line description

    If format begins with white space it will be stripped

    Args:
        description(str): Description from a vcf header line

    Return:
        format(str): The format information from description
    """
    description = description.strip('"')
    keyword = "Format:"
    before_keyword, keyword, after_keyword = description.partition(keyword)
    return after_keyword.strip()


def parse_vep_header(vcf_obj):
    """Return a list with the VEP header

    The vep header is collected from CSQ in the vcf file
    All keys are capitalized

    Args:
        vcf_obj(cyvcf2.VCF)

    Returns:
        vep_header(list)
    """
    vep_header = []

    if "CSQ" in vcf_obj:
        # This is a dictionary
        csq_info = vcf_obj["CSQ"]
        format_info = parse_header_format(csq_info["Description"])
        vep_header = [key.upper() for key in format_info.split("|")]

    return vep_header
