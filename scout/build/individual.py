import logging
import os

from scout.constants import ANALYSIS_TYPES, REV_PHENOTYPE_MAP, REV_SEX_MAP
from scout.exceptions import PedigreeError

log = logging.getLogger(__name__)
BUILD_INDIVIDUAL_FILES = [
    "bam_file",
    "d4_file",
    "mitodel_file",
    "mt_bam",
    "rhocall_bed",
    "rhocall_wig",
    "rna_alignment_path",
    "rna_coverage_bigwig",
    "splice_junctions_bed",
    "tiddit_coverage_wig",
    "upd_regions_bed",
    "upd_sites_bed",
    "vcf2cytosure",
]


def set_abspath_individual_file(ind_obj: dict, ind: dict, ind_file: str):
    """Fix absolute path for individual files to be served from application.
    This takes care of incomplete path for demo files. While most endpoints would attempt to make an
    abs path when sending, storing them as absolute if we can access them on cli load ensures that
    we can still find them from the web app later, even if that happens to be started in another working directory.

    This may close a loophole for some very particular use cases, but in general should be safer.
    """

    file_path = ind.get(ind_file)
    if file_path and os.path.exists(file_path):
        ind_obj[ind_file] = os.path.abspath(file_path)
    else:
        ind_obj[ind_file] = None


def set_abspath_nested_individual_files(ind_obj: dict, ind: dict, nested_file_key: str):
    """Fix absolute path for nested files to be served from application.
    For some of our more complicated nesting, e.g. Chromograph, the file endings are generalised lat (in js),
    and only a template is stored on the individual object. We then still wish to update the dirname, treating the
    basename lightly as a template without checking for file existence just yet. The endpoints will handle that later.
    """
    if ind.get(nested_file_key):
        ind_obj[nested_file_key] = ind.get(nested_file_key)
        for nested_file_item in ind_obj[nested_file_key]:
            if nested_file_item:
                if os.path.exists(nested_file_item):
                    ind_obj[nested_file_key][nested_file_item] = os.path.abspath(nested_file_item)
                    continue

                nested_file_item_dirname = os.path.dirname(nested_file_item)
                nested_file_item_basename = os.path.basename(nested_file_item)
                ind_obj[nested_file_key][nested_file_item] = (
                    os.path.abspath(nested_file_item_dirname) + "/" + nested_file_item_basename
                )


def build_individual(ind: dict) -> dict:
    """Build an Individual object

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
        rna_coverage_bigwig = str, # Path to coverage islands file (RNA analysis)
        splice_junctions_bed = str, # Path to indexed junctions .bed.gz file obtained from STAR v2 aligner *.SJ.out.tab file.
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

    ind_obj["subject_id"] = ind.get("subject_id", None)

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

    for ind_file in BUILD_INDIVIDUAL_FILES:
        set_abspath_individual_file(ind_obj, ind, ind_file)

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

    ind_obj["mitodel"] = ind.get("mitodel")

    ind_obj["chromograph_images"] = ind.get("chromograph_images")
    ind_obj["reviewer"] = ind.get("reviewer")

    for nested_file_key in "chromograph_images", "reviewer":
        set_abspath_nested_individual_files(ind_obj, ind, nested_file_key)

    # Check if the analysis type is ok
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

    # BioNano FSHD
    ind_obj["bionano_access"] = ind.get("bionano_access", None)
    ind_obj["fshd_loci"] = ind.get("fshd_loci", None)

    return ind_obj
