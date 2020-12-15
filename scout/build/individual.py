import logging
import os

from scout.constants import REV_PHENOTYPE_MAP, REV_SEX_MAP, ANALYSIS_TYPES
from scout.exceptions import PedigreeError

log = logging.getLogger(__name__)


def build_individual(ind):
    """Build a Individual object

    Args:
        ind (dict): A dictionary with individual information

    Returns:
        ind_obj (dict): A Individual object

    Raises:
        PedigreeError: if sex is unknown,
        if phenotype is unknown,
        if analysis_type is unknwon,
        or missing individual_id

    dict(
        individual_id = str, # required
        display_name = str,
        sex = str,
        phenotype = int,
        father = str, # Individual id of father
        mother = str, # Individual id of mother
        capture_kits = list, # List of names of capture kits
        bam_file = str, # Path to bam file,
        rhocall_wig = str, # Path to a rhocall wig file showing heterozygosity levels
        rhocall_bed = str, # Path to a rhocall bed file marking LOH regions
        tiddit_coverage_wig = str, # Path to a TIDDIT coverage wig - overview coverage
        upd_regions_bed = str, # Path to a UPD regions bed marking UPD calls
        upd_sites_bed = str, # Path to a UPD sites bed, showing UPD info for vars
        vcf2cytosure = str, # Path to CGH file
        is_sma = boolean,
        is_sma_carrier = boolean,
        smn1_cn = int,
        smn2_cn = int,
        smn2delta78_cn = int,
        smn_27134_cn = int,
        predicted_ancestry = str,
        analysis_type = str, # choices=ANALYSIS_TYPES
    )
    """
    try:
        ind_obj = dict(individual_id=ind["individual_id"])
        log.info("Building Individual with id:{0}".format(ind["individual_id"]))
    except KeyError as err:
        raise PedigreeError("Individual is missing individual_id")

    # Use individual_id if display_name does not exist
    ind_obj["display_name"] = ind.get("display_name", ind_obj["individual_id"])

    sex = ind.get("sex", "unknown")
    # Convert sex to .ped
    try:
        # Check if sex is coded as an integer
        int(sex)
        ind_obj["sex"] = str(sex)
    except ValueError as err:
        try:
            # Sex are numbers in the database
            ind_obj["sex"] = REV_SEX_MAP[sex]
        except KeyError as err:
            raise (PedigreeError("Unknown sex: %s" % sex))

    phenotype = ind.get("phenotype", "unknown")
    # Make the phenotype integers
    try:
        ped_phenotype = REV_PHENOTYPE_MAP[phenotype]
        if ped_phenotype == -9:
            ped_phenotype = 0
        ind_obj["phenotype"] = ped_phenotype
    except KeyError as err:
        raise (PedigreeError("Unknown phenotype: %s" % phenotype))

    # Fix absolute path for individual bam files (takes care of incomplete path for demo files)
    ind_files = [
        "bam_file",
        "mt_bam",
        "vcf2cytosure",
        "rhocall_bed",
        "rhocall_wig",
        "tiddit_coverage_wig",
        "upd_regions_bed",
        "upd_sites_bed"
    ]

    for ind_file in ind_files:
        file_path = ind.get(ind_file)
        if file_path and os.path.exists(file_path):
            ind_obj[ind_file] = os.path.abspath(file_path)
        else:
            ind_obj[ind_file] = None

    ind_obj["father"] = ind.get("father")
    ind_obj["mother"] = ind.get("mother")
    ind_obj["capture_kits"] = ind.get("capture_kits", [])
    ind_obj["confirmed_sex"] = ind.get("confirmed_sex")
    ind_obj["confirmed_parent"] = ind.get("confirmed_parent")
    ind_obj["predicted_ancestry"] = ind.get("predicted_ancestry")
    ind_obj['chromograph_images'] = ind.get("chromograph_images")


    # Check if the analysis type is ok
    # Can be anyone of ('wgs', 'wes', 'mixed', 'unknown')
    analysis_type = ind.get("analysis_type", "unknown")
    if not analysis_type in ANALYSIS_TYPES:
        raise PedigreeError("Analysis type %s not allowed", analysis_type)
    ind_obj["analysis_type"] = analysis_type

    if "tmb" in ind:
        ind_obj["tmb"] = ind["tmb"]

    if "msi" in ind:
        ind_obj["msi"] = ind["msi"]

    if "tumor_purity" in ind:
        ind_obj["tumor_purity"] = ind["tumor_purity"]

    if "tumor_type" in ind:
        ind_obj["tumor_type"] = ind["tumor_type"]

    ind_obj["tissue_type"] = ind.get("tissue_type", "unknown")

    # SMA
    ind_obj["is_sma"] = ind.get("is_sma", None)
    ind_obj["is_sma_carrier"] = ind.get("is_sma_carrier", None)
    ind_obj["smn1_cn"] = ind.get("smn1_cn", None)
    ind_obj["smn2_cn"] = ind.get("smn2_cn", None)
    ind_obj["smn2delta78_cn"] = ind.get("smn2delta78_cn", None)
    ind_obj["smn_27134_cn"] = ind.get("smn_27134_cn", None)

    return ind_obj
