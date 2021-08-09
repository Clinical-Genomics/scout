import copy
import datetime
import logging
from fractions import Fraction
from pathlib import Path
from pprint import pprint as pp

from ped_parser import FamilyParser

from scout.constants import PHENOTYPE_MAP, REV_PHENOTYPE_MAP, REV_SEX_MAP, SEX_MAP
from scout.exceptions import ConfigError, PedigreeError
from scout.parse.peddy import parse_peddy_ped, parse_peddy_ped_check, parse_peddy_sex_check
from scout.parse.smn import parse_smn_file
from scout.utils.date import get_date

LOG = logging.getLogger(__name__)


def get_correct_date(date_info):
    """Convert dateinfo to correct date

    Args:
        dateinfo: Something that represents a date

    Returns:
        correct_date(datetime.datetime)
    """
    if isinstance(date_info, datetime.datetime):
        return date_info

    if isinstance(date_info, str):
        try:
            correct_date = get_date(date_info)
        except ValueError as err:
            LOG.warning("Analysis date is on wrong format")
            LOG.info("Setting analysis date to todays date")
            correct_date = datetime.datetime.now()
        return correct_date

    LOG.info("Setting analysis date to todays date")
    return datetime.datetime.now()


def parse_custom_images(config_data):
    """Parse information on custom images assigned to the case."""
    VALID_IMAGE_SUFFIXES = ["gif", "svg", "png", "jpg", "jpeg"]
    LOG.debug("Parse custom images")

    # sort custom image sections
    parsed_sections = {}
    for section_name, images in config_data.get("custom_images", {}).items():
        parsed_images = []
        for image in images:
            # skip entries that are not recognized as image on suffix
            path = Path(image["path"])
            if not path.suffix[1:] in VALID_IMAGE_SUFFIXES:
                LOG.warning(f"Image: {path.name} is not recognized as an image, skipping")
                continue
            # load image file to memory
            with open(image["path"], "rb") as image_file:
                parsed_images.append(
                    {
                        "title": image["title"],
                        "description": image["description"],
                        "data": bytes(image_file.read()),
                        "width": image.get("width"),
                        "height": image.get("height"),
                        "format": "svg+xml" if path.suffix[1:] == "svg" else path.suffix[1:],
                    }
                )
        # store parsed section
        if len(parsed_images) > 0:
            parsed_sections[section_name] = parsed_images
        else:
            LOG.warning(f"Section: {section_name} had no valid images, skipping")
    return parsed_sections


def parse_case_data(
    config=None,
    ped=None,
    owner=None,
    vcf_snv=None,
    vcf_sv=None,
    vcf_cancer=None,
    vcf_cancer_sv=None,
    vcf_str=None,
    smn_tsv=None,
    peddy_ped=None,
    peddy_sex=None,
    peddy_check=None,
    delivery_report=None,
    multiqc=None,
    cnv_report=None,
    coverage_qc_report=None,
    gene_fusion_report=None,
    gene_fusion_report_research=None,
):
    """Parse all data necessary for loading a case into scout

    This can be done either by providing a VCF file and other information
    on the command line. Or all the information can be specified in a config file.
    Please see Scout documentation for further instructions.

    Args:
        config(dict): A yaml formatted config file
        ped(iterable(str)): A ped formatted family file
        owner(str): The institute that owns a case
        vcf_snv(str): Path to a vcf file
        vcf_str(str): Path to a VCF file
        vcf_sv(str): Path to a vcf file
        vcf_cancer(str): Path to a vcf file
        vcf_cancer_sv(str): Path to a vcf file
        smn_tsv(str): Path to an SMN tsv file
        peddy_ped(str): Path to a peddy ped
        multiqc(str): Path to dir with multiqc information
        cnv_report: Path to pdf file with CNV report
        coverage_qc_report: Path to html file with coverage and qc report
        gene_fusion_report: Path to the gene fusions report
        gene_fusion_report_research: Path to the gene fusions research report

    Returns:
        config_data(dict): Holds all the necessary information for loading
                           Scout
    """
    config_data = copy.deepcopy(config) or {}
    # Default the analysis date to now if not specified in load config
    config_data["analysis_date"] = get_correct_date(config_data.get("analysis_date"))

    # If the family information is in a ped file we nned to parse that
    if ped:
        family_id, samples = parse_ped(ped)
        config_data["family"] = family_id
        config_data["samples"] = samples

    # Each case has to have a owner. If not provided in config file it needs to be given as a
    # argument
    if "owner" not in config_data:
        if not owner:
            raise SyntaxError("Case has no owner")

        config_data["owner"] = owner

    if "gene_panels" in config_data:
        # handle whitespace in gene panel names
        config_data["gene_panels"] = [panel.strip() for panel in config_data["gene_panels"]]
        config_data["default_gene_panels"] = [
            panel.strip() for panel in config_data["default_gene_panels"]
        ]

    # handle scout/commands/load/case.py
    config_data["custom_images"] = parse_custom_images(config_data)

    ##################### Add information from peddy if existing #####################
    config_data["peddy_ped"] = peddy_ped or config_data.get("peddy_ped")
    config_data["peddy_sex_check"] = peddy_sex or config_data.get("peddy_sex")
    config_data["peddy_ped_check"] = peddy_check or config_data.get("peddy_check")

    # This will add information from peddy to the individuals
    add_peddy_information(config_data)

    ##################### Add multiqc information #####################
    config_data["multiqc"] = multiqc or config_data.get("multiqc")

    config_data["vcf_snv"] = vcf_snv if vcf_snv else config_data.get("vcf_snv")
    config_data["vcf_sv"] = vcf_sv if vcf_sv else config_data.get("vcf_sv")
    config_data["vcf_str"] = vcf_str if vcf_str else config_data.get("vcf_str")
    config_data["smn_tsv"] = smn_tsv if smn_tsv else config_data.get("smn_tsv")

    LOG.debug("Checking for SMN TSV..")
    if config_data["smn_tsv"]:
        LOG.info("Adding SMN info from {}.".format(config_data["smn_tsv"]))
        add_smn_info(config_data)

    config_data["vcf_cancer"] = vcf_cancer if vcf_cancer else config_data.get("vcf_cancer")
    config_data["vcf_cancer_sv"] = (
        vcf_cancer_sv if vcf_cancer_sv else config_data.get("vcf_cancer_sv")
    )

    config_data["delivery_report"] = (
        delivery_report if delivery_report else config_data.get("delivery_report")
    )

    config_data["cnv_report"] = cnv_report if cnv_report else config_data.get("cnv_report")
    config_data["coverage_qc_report"] = (
        coverage_qc_report if coverage_qc_report else config_data.get("coverage_qc_report")
    )
    config_data["gene_fusion_report"] = (
        gene_fusion_report if gene_fusion_report else config_data.get("gene_fusion_report")
    )
    config_data["gene_fusion_report_research"] = (
        gene_fusion_report_research
        if gene_fusion_report_research
        else config_data.get("gene_fusion_report_research")
    )

    config_data["rank_model_version"] = str(config_data.get("rank_model_version", ""))
    config_data["rank_score_threshold"] = config_data.get("rank_score_threshold", 0)

    config_data["sv_rank_model_version"] = str(config_data.get("sv_rank_model_version", ""))

    config_data["track"] = config_data.get("track", "rare")
    if config_data["vcf_cancer"] or config_data["vcf_cancer_sv"]:
        config_data["track"] = "cancer"

    return config_data


def add_smn_info(config_data):
    """Add SMN CN / SMA prediction from TSV files to individuals

    Args:
        config_data(dict)
    """

    if not config_data.get("smn_tsv"):
        LOG.warning("No smn_tsv though add_smn_info called. This is odd.")
        return

    file_handle = open(config_data["smn_tsv"], "r")
    smn_info = {}
    for smn_ind_info in parse_smn_file(file_handle):
        smn_info[smn_ind_info["sample_id"]] = smn_ind_info

    for ind in config_data["samples"]:
        ind_id = ind["sample_id"]
        try:
            for key in [
                "is_sma",
                "is_sma_carrier",
                "smn1_cn",
                "smn2_cn",
                "smn2delta78_cn",
                "smn_27134_cn",
            ]:
                ind[key] = smn_info[ind_id][key]
        except KeyError as e:
            LOG.warning("Individual {} has no SMN info to update: {}.".format(ind_id, e))


def add_smn_info_case(case_data):
    """Add SMN CN / SMA prediction from TSV files to individuals in a yaml load case context

    Args:
        case_data(dict)
    """

    if not case_data.get("smn_tsv"):
        LOG.warning("No smn_tsv though add_smn_info_case called. This is odd.")
        return

    file_handle = open(case_data["smn_tsv"], "r")
    smn_info = {}
    for smn_ind_info in parse_smn_file(file_handle):
        smn_info[smn_ind_info["sample_id"]] = smn_ind_info

    for ind in case_data["individuals"]:
        ind_id = ind["individual_id"]
        try:
            for key in [
                "is_sma",
                "is_sma_carrier",
                "smn1_cn",
                "smn2_cn",
                "smn2delta78_cn",
                "smn_27134_cn",
            ]:
                ind[key] = smn_info[ind_id][key]
        except KeyError as e:
            LOG.warning("Individual {} has no SMN info to update: {}.".format(ind_id, e))


def add_peddy_information(config_data):
    """Add information from peddy outfiles to the individuals

    Args:
        config_data(dict)
    """
    ped_info = {}
    ped_check = {}
    sex_check = {}
    relations = []

    if config_data.get("peddy_ped"):
        file_handle = open(config_data["peddy_ped"], "r")
        for ind_info in parse_peddy_ped(file_handle):
            ped_info[ind_info["sample_id"]] = ind_info

    if config_data.get("peddy_ped_check"):
        file_handle = open(config_data["peddy_ped_check"], "r")
        for pair_info in parse_peddy_ped_check(file_handle):
            ped_check[(pair_info["sample_a"], pair_info["sample_b"])] = pair_info

    if config_data.get("peddy_sex_check"):
        file_handle = open(config_data["peddy_sex_check"], "r")
        for ind_info in parse_peddy_sex_check(file_handle):
            sex_check[ind_info["sample_id"]] = ind_info

    if not ped_info:
        return

    analysis_inds = {}
    for ind in config_data["samples"]:
        ind_id = ind["sample_id"]
        analysis_inds[ind_id] = ind

    for ind_id in analysis_inds:
        ind = analysis_inds[ind_id]
        # Check if peddy has inferred the ancestry
        if ind_id in ped_info:
            ind["predicted_ancestry"] = ped_info[ind_id].get("ancestry-prediction", "UNKNOWN")
        # Check if peddy has inferred the sex
        if ind_id in sex_check:
            if sex_check[ind_id]["error"]:
                ind["confirmed_sex"] = False
            else:
                ind["confirmed_sex"] = True

        # Check if peddy har confirmed parental relations
        for parent in ["mother", "father"]:
            # If we are looking at individual with parents
            if ind[parent] == "0":
                continue
            # Check if the child/parent pair is in peddy data
            for pair in ped_check:
                if not (ind_id in pair and ind[parent] in pair):
                    continue
                # If there is a parent error we mark that
                if ped_check[pair]["parent_error"]:
                    analysis_inds[ind[parent]]["confirmed_parent"] = False
                    continue
                # Else if parent confirmation has not been done
                if "confirmed_parent" not in analysis_inds[ind[parent]]:
                    # Set confirmatio to True
                    analysis_inds[ind[parent]]["confirmed_parent"] = True


def parse_individual(sample):
    """Parse individual information

    Args:
        sample (dict)

    Returns:
        {
            'individual_id': str,
            'father': str,
            'mother': str,
            'display_name': str,
            'sex': str,
            'phenotype': str,
            'bam_file': str,
            'mt_bam': str,
            'analysis_type': str,
            'vcf2cytosure': str,
            'capture_kits': list(str),
            'upd_sites_bed': str,
            'upd_regions_bed': str,
            'rhocall_bed': str,
            'rhocall_wig': str,
            'tiddit_coverage_wig': str,
            'predicted_ancestry' = str,
            'is_sma': boolean,
            'is_sma_carrier': boolean,
            'smn1_cn' = int,
            'smn2_cn' = int,
            'smn2delta78_cn' = int,
            'smn_27134_cn' = int,
            'tumor_type': str,
            'tmb': str,
            'msi': str,
            'tumor_purity': float,
            'tissue_type': str,
            'chromograph_images': str
            'vcf2cytosure': str
            'rna_coverage_bigwig': str
            'splice_junctions_bed': str
        }

    """
    ind_info = {}
    if "sample_id" not in sample:
        raise PedigreeError("One sample is missing 'sample_id'")
    sample_id = sample["sample_id"]
    # Check the sex
    if "sex" not in sample:
        raise PedigreeError("Sample %s is missing 'sex'" % sample_id)
    sex = sample["sex"]
    if sex not in REV_SEX_MAP:
        LOG.warning(
            "'sex' is only allowed to have values from {}".format(
                ", ".join(list(REV_SEX_MAP.keys()))
            )
        )
        raise PedigreeError("Individual %s has wrong formated sex" % sample_id)

    # Check the phenotype
    if "phenotype" not in sample:
        raise PedigreeError("Sample %s is missing 'phenotype'" % sample_id)
    phenotype = sample["phenotype"]
    if phenotype not in REV_PHENOTYPE_MAP:
        LOG.warning(
            "'phenotype' is only allowed to have values from {}".format(
                ", ".join(list(REV_PHENOTYPE_MAP.keys()))
            )
        )
        raise PedigreeError("Individual %s has wrong formated phenotype" % sample_id)

    ind_info["individual_id"] = sample_id
    ind_info["display_name"] = sample.get("sample_name", sample["sample_id"])

    ind_info["sex"] = sex
    ind_info["phenotype"] = phenotype

    ind_info["father"] = sample.get("father")
    ind_info["mother"] = sample.get("mother")

    ind_info["confirmed_parent"] = sample.get("confirmed_parent")
    ind_info["confirmed_sex"] = sample.get("confirmed_sex")
    ind_info["predicted_ancestry"] = sample.get("predicted_ancestry")

    # IGV files these can be bam or cram format
    bam_path_options = ["alignment_path", "bam_path", "bam_file"]
    for option in bam_path_options:
        if sample.get(option) and not sample.get(option).strip() == "":
            if "bam_file" in ind_info:
                LOG.warning(
                    "Multiple alignment paths given for individual %s in load config. Using %s",
                    ind_info["individual_id"],
                    ind_info["bam_file"],
                )
            else:
                ind_info["bam_file"] = sample[option]

    ind_info["rhocall_bed"] = sample.get("rhocall_bed", sample.get("rhocall_bed"))
    ind_info["rhocall_wig"] = sample.get("rhocall_wig", sample.get("rhocall_wig"))
    ind_info["tiddit_coverage_wig"] = sample.get(
        "tiddit_coverage_wig", sample.get("tiddit_coverage_wig")
    )
    ind_info["upd_regions_bed"] = sample.get("upd_regions_bed", sample.get("upd_regions_bed"))
    ind_info["upd_sites_bed"] = sample.get("upd_sites_bed", sample.get("upd_sites_bed"))
    ind_info["mt_bam"] = sample.get("mt_bam")
    ind_info["analysis_type"] = sample.get("analysis_type")

    # Path to downloadable vcf2cytosure file
    ind_info["vcf2cytosure"] = sample.get("vcf2cytosure")

    # Path to splice junctions data
    ind_info["rna_coverage_bigwig"] = sample.get("rna_coverage_bigwig")
    ind_info["splice_junctions_bed"] = sample.get("splice_junctions_bed")

    # load sma file if it is not done at this point!
    ind_info["is_sma"] = sample.get("is_sma", None)
    ind_info["is_sma_carrier"] = sample.get("is_sma_carrier", None)
    ind_info["smn1_cn"] = sample.get("smn1_cn", None)
    ind_info["smn2_cn"] = sample.get("smn2_cn", None)
    ind_info["smn2delta78_cn"] = sample.get("smn2delta78_cn", None)
    ind_info["smn_27134_cn"] = sample.get("smn_27134_cn", None)

    ind_info["capture_kits"] = [sample.get("capture_kit")] if "capture_kit" in sample else []

    # Cancer specific values
    ind_info["tumor_type"] = sample.get("tumor_type")
    # tumor_mutational_burden
    ind_info["tmb"] = sample.get("tmb")
    ind_info["msi"] = sample.get("msi")

    ind_info["tumor_purity"] = sample.get("tumor_purity")
    # might be a string-formatted fraction, example: 30/90
    if isinstance(ind_info["tumor_purity"], str):
        ind_info["tumor_purity"] = float(Fraction(ind_info["tumor_purity"]))

    ind_info["tissue_type"] = sample.get("tissue_type")

    ind_info["chromograph_images"] = sample.get("chromograph_images")

    # Remove key-value pairs from ind_info where key==None and return
    return removeNoneValues(ind_info)


def parse_individuals(samples):
    """Parse the individual information

    Reformat sample information to proper individuals

    Args:
        samples(list(dict))

    Returns:
        individuals(list(dict))
    """
    individuals = []
    if len(samples) == 0:
        raise PedigreeError("No samples could be found")

    ind_ids = set()
    for sample_info in samples:
        parsed_ind = parse_individual(sample_info)
        individuals.append(parsed_ind)
        ind_ids.add(parsed_ind["individual_id"])

    # Check if relations are correct
    for parsed_ind in individuals:
        father = parsed_ind.get("father")
        if father and father != "0":
            if father not in ind_ids:
                raise PedigreeError("father %s does not exist in family" % father)
        mother = parsed_ind.get("mother")
        if mother and mother != "0":
            if mother not in ind_ids:
                raise PedigreeError("mother %s does not exist in family" % mother)

    return individuals


def parse_case(config):
    """Parse case information from config or PED files.

    Args:
        config (dict): case config with detailed information

    Returns:
        dict: parsed case data
    """
    if "owner" not in config:
        raise ConfigError("A case has to have a owner")

    if "family" not in config:
        raise ConfigError("A case has to have a 'family'")

    individuals = parse_individuals(config["samples"])
    synopsis = None
    if config.get("synopsis"):
        synopsis = (
            ". ".join(config["synopsis"])
            if isinstance(config["synopsis"], list)
            else config["synopsis"]
        )

    case_data = {
        "owner": config["owner"],
        "collaborators": [config["owner"]],
        "case_id": config["family"],
        "display_name": config.get("family_name", config["family"]),
        "synopsis": synopsis,
        "phenotype_terms": config.get("phenotype_terms"),
        "cohorts": config.get("cohorts"),
        "genome_build": config.get("human_genome_build"),
        "lims_id": config.get("lims_id"),
        "rank_model_version": str(config.get("rank_model_version", "")),
        "rank_score_threshold": config.get("rank_score_threshold", 0),
        "sv_rank_model_version": str(config.get("sv_rank_model_version", "")),
        "analysis_date": config.get("analysis_date"),
        "individuals": individuals,
        "vcf_files": {
            "vcf_snv": config.get("vcf_snv"),
            "vcf_sv": config.get("vcf_sv"),
            "vcf_str": config.get("vcf_str"),
            "vcf_cancer": config.get("vcf_cancer"),
            "vcf_cancer_sv": config.get("vcf_cancer_sv"),
            "vcf_snv_research": config.get("vcf_snv_research"),
            "vcf_sv_research": config.get("vcf_sv_research"),
            "vcf_cancer_research": config.get("vcf_cancer_research"),
            "vcf_cancer_sv_research": config.get("vcf_cancer_sv_research"),
        },
        "smn_tsv": config.get("smn_tsv"),
        "default_panels": config.get("default_gene_panels", []),
        "gene_panels": config.get("gene_panels", []),
        "assignee": config.get("assignee"),
        "peddy_ped": config.get("peddy_ped"),
        "peddy_sex": config.get("peddy_sex"),
        "peddy_check": config.get("peddy_check"),
        "delivery_report": config.get("delivery_report"),
        "cnv_report": config.get("cnv_report"),
        "coverage_qc_report": config.get("coverage_qc_report"),
        "gene_fusion_report": config.get("gene_fusion_report"),
        "gene_fusion_report_research": config.get("gene_fusion_report_research"),
        "multiqc": config.get("multiqc"),
        "track": config.get("track", "rare"),
        "custom_images": config.get("custom_images", {}),
    }

    # add SMN info
    LOG.debug("Checking for SMN TSV..")
    if case_data["smn_tsv"]:
        LOG.info("Adding SMN info from {}.".format(case_data["smn_tsv"]))
        add_smn_info_case(case_data)

    # add the pedigree figure, this is a xml file which is dumped in the db
    if "madeline" in config:
        mad_path = Path(config["madeline"])
        if not mad_path.exists():
            raise ValueError("madeline path not found: {}".format(mad_path))
        with mad_path.open("r") as in_handle:
            case_data["madeline_info"] = in_handle.read()

    if (
        case_data["vcf_files"]["vcf_cancer"]
        or case_data["vcf_files"]["vcf_cancer_research"]
        or case_data["vcf_files"]["vcf_cancer_sv"]
        or case_data["vcf_files"]["vcf_cancer_sv_research"]
    ):
        case_data["track"] = "cancer"

    case_data["analysis_date"] = get_correct_date(case_data.get("analysis_date"))

    return case_data


def parse_ped(ped_stream, family_type="ped"):
    """Parse out minimal family information from a PED file.

    Args:
        ped_stream(iterable(str))
        family_type(str): Format of the pedigree information

    Returns:
        family_id(str), samples(list[dict])
    """
    pedigree = FamilyParser(ped_stream, family_type=family_type)

    if len(pedigree.families) != 1:
        raise PedigreeError("Only one case per ped file is allowed")

    family_id = list(pedigree.families.keys())[0]
    family = pedigree.families[family_id]

    samples = [
        {
            "sample_id": ind_id,
            "father": individual.father,
            "mother": individual.mother,
            # Convert sex to human readable
            "sex": SEX_MAP[individual.sex],
            "phenotype": PHENOTYPE_MAP[int(individual.phenotype)],
        }
        for ind_id, individual in family.individuals.items()
    ]

    return family_id, samples


def removeNoneValues(dictionary):
    """If value = None in key/value pair, the pair is removed.
        Python >3
    Args:
        dictionary: dict

    Returns:
        dict
    """

    return {k: v for k, v in dictionary.items() if v is not None}
