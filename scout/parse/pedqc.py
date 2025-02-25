from typing import List

from scout.utils.convert import convert_number, make_bool


def tsv_to_info_dicts(
    lines: List[str], separator: str = "\t", number_keys: List[str] = [], bool_keys: List[str] = []
) -> List[dict]:
    """Parse a tsv (or csv with "," as separator) file to a list of dicts, with the header fields as dict keys,
    column values as dict values, and each list item one such dict for each row.
    The number_keys and bool_keys are lists of key names to attempt to explicitly coerce values into number or bool before return.
    """
    info_dicts = []
    for i, line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            header = line.lstrip("#").split(separator)
            continue
        info_dict = dict(zip(header, line.split(separator)))
        for number_key in number_keys:
            if number_key in info_dict:
                info_dict[number_key] = convert_number(info_dict[number_key])
        for bool_key in bool_keys:
            if bool_key in info_dict:
                info_dict[bool_key] = make_bool(info_dict.get(bool_key))
        info_dicts.append(info_dict)

    return info_dicts


def parse_peddy_ped(lines: List[str]) -> List[dict]:
    """Parse a peddy.ped file

    ancestry-prediction: one of AFR AMR EAS EUR SAS UNKNOWN
    PC1/PC2/PC3/PC4: the first 4 values after this sample was
                    projected onto the thousand genomes principal components.

    idr_baf: inter-decile range (90th percentile - 10th percentile)
             of b-allele frequency. We make a distribution of all sites of
             alts / (ref + alts) and then report the difference between the
             90th and the 10th percentile.
             Large values indicated likely sample contamination.
    """
    return tsv_to_info_dicts(
        lines,
        "\t",
        number_keys=["PC1", "PC2", "PC3", "het_call_rate", "het_idr_baf", "het_mean_depth"],
    )


def parse_peddy_ped_check(lines: List[str]) -> List[dict]:
    """Parse a .ped_check.csv file

    The following keys are explicitly coerced upon insertion into the returned dicts
            hets_a  - the number of sites at which sample_a was heterozygous
            hets_b  - the number of sites at which sample_b was heterozygous
            ibs0    - the number of sites at which the 2 samples shared no alleles
                    (should approach 0 for parent-child pairs).
            ibs2    - the number of sites and which the 2 samples where both
                    hom-ref, both het, or both hom-alt.
            n       - the number of sites that was used to predict the relatedness.
            rel     - the relatedness reported in the ped file.
            pedigree_relatedness - the relatedness reported in the ped file.
            rel_difference - difference between the preceding 2 columns.
            shared_hets - the number of sites at which both samples were hets.

            pedigree_parents - boolean indicating that this pair is a parent-child pair
                    according to the ped file.
            predicted_parents - boolean indicating that this pair is expected to be a parent-child
                    pair according to the ibs0 (< 0.012) calculated from the genotypes.
            parent_error - boolean indicating that the preceding 2 columns do not match
            sample_duplication_error - boolean indicating that rel > 0.75 and ibs0 < 0.012
    """
    return tsv_to_info_dicts(
        lines,
        ",",
        number_keys=[
            "hets_a",
            "hets_b",
            "ibs0",
            "ibs2",
            "n",
            "rel",
            "pedigree_relatedness",
            "rel_difference",
            "shared_hets",
        ],
        bool_keys=[
            "pedigree_parents",
            "predicted_parents",
            "parent_error",
            "sample_duplication_error",
        ],
    )


def parse_peddy_sex_check(lines: List[str]) -> List[dict]:
    """Parse a .ped_check.csv file

    Type coerce the following keys for each dict in the returned sex_check dict:
        error: boolean indicating whether there is a mismatch between chr genotypes and ped sex
        hom_alt_count: number of homozygous-alternate calls
        hom_ref_count: number of homozygous-reference calls
        het_count:  number of heterozygote calls
        het_ratio: ratio of het_count / hom_alt_count. Low for males, high for females
    """
    return tsv_to_info_dicts(
        lines,
        ",",
        number_keys=["hom_alt_count", "hom_ref_count", "het_count", "het_ratio"],
        bool_keys=["error"],
    )


def parse_somalier_pairs(lines: List[str]) -> List[dict]:
    """Parse a Somalier pairs tsv file"""
    return tsv_to_info_dicts(lines, "\t", ["relatedness", "ibs0", "ibs2"])


def parse_somalier_samples(lines: List[str]) -> List[dict]:
    """Parse a Somalier samples tsv file"""
    return tsv_to_info_dicts(lines, "\t")


def parse_somalier_ancestry(lines: List[str]) -> List[dict]:
    """Parse a Somalier ancestry tsv file"""
    return tsv_to_info_dicts(lines, "\t")
