import copy
import datetime
import logging
from pathlib import Path
from pprint import pprint as pp
from fractions import Fraction

from ped_parser import FamilyParser

from scout.constants import PHENOTYPE_MAP, REV_PHENOTYPE_MAP, REV_SEX_MAP, SEX_MAP
from scout.exceptions import ConfigError, PedigreeError

from scout.parse.peddy import (
    parse_peddy_ped,
    parse_peddy_ped_check,
    parse_peddy_sex_check,
)
from scout.parse.smn import parse_smn_file
from scout.utils.date import get_date

from scout.parse.config_base import ScoutLoadConfig, ScoutIndividual, VcfFiles

LOG = logging.getLogger(__name__)


def get_correct_date(date_info):
    """Convert dateinfo to correct date

    Args:
        dateinfo: Something that represents a date

    Returns:
        correct_date(datetime.datetime)
    """
    LOG.debug(date_info)
    if isinstance(date_info, str):
        LOG.debug("STRINIGNIGGNIGNDIREKT")
    if isinstance(date_info, datetime.datetime):
        LOG.debug("CORRECT DIREKT")
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


def parse_case_data(**kwargs):
    """Parse all data necessary for loading a case into scout

    This can be done either by providing a VCF file and other information
    on the command line. Or all the information can be specified in a config file.
    Please see Scout documentation for further instructions.

    Possible keyword args:
        cnv_report: Path to pdf file with CNV report
        config(dict): A yaml formatted config file
        coverage_qc_report: Path to html file with coverage and qc report
        multiqc(str): Path to dir with multiqc information
        owner(str): The institute that owns a case
        ped(iterable(str)): A ped formatted family file
        peddy_ped(str): Path to a peddy ped
        smn_tsv(str): Path to an SMN tsv file
        vcf_cancer(str): Path to a vcf file
        vcf_cancer_sv(str): Path to a vcf file
        vcf_snv(str): Path to a vcf file
        vcf_str(str): Path to a VCF file
        vcf_sv(str): Path to a vcf file

    Returns:
        config_data(dict): Holds all the necessary information for loading
                           Scout
    """
    config = kwargs.pop("config", {})
    
    # If ped file  provided we need to parse that first
    if "ped" in kwargs and kwargs["ped"] is not None:
        family_id, samples = parse_ped(kwargs["ped"])
        config["family"] = family_id
        config["samples"] = samples

    # Give passed keyword arguments precedence over file configuration
    # Except for 'owner', prededence config file over arguments
    LOG.debug("KWARGS: {}".format(kwargs))
    if "owner" in config:
        print(kwargs)
        kwargs.pop("owner", None)  # dont crash if 'owner' is missing
    for key in kwargs:
        if kwargs[key] is not None:
            config[key] = kwargs[key]
        else:
            try:
                config[key] = config[key]
            except KeyError:
                config[key] = None

    # populate configuration according to Pydantic defined classes
    LOG.debug("1st SCOUTLOADCONFIG")
    config = ScoutLoadConfig(**config)

    # convert to dict
    config = config.dict()

    synopsis = (
        ". ".join(config["synopsis"])
        if isinstance(config["synopsis"], list)
        else config["synopsis"]
    )

    # Default the analysis date to now if not specified in load config
    config["analysis_date"] = get_correct_date(config.get("analysis_date"))
    # handle whitespace in gene panel names
    try:
        config["gene_panels"] = [panel.strip() for panel in config["gene_panels"]]
        config["default_gene_panels"] = [
            panel.strip() for panel in config["default_gene_panels"]
        ]
    except:
        pass

    # This will add information from peddy to the individuals
    add_peddy_information(config)

    ##################### Add multiqc information #####################
    LOG.debug("Checking for SMN TSV..")
    if config["smn_tsv"]:
        LOG.info("Adding SMN info from {}.".format(config["smn_tsv"]))
        add_smn_info(config)

    return removeNoneRecursive(config)


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
            LOG.warning(
                "Individual {} has no SMN info to update: {}.".format(ind_id, e)
            )


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
            LOG.warning(
                "Individual {} has no SMN info to update: {}.".format(ind_id, e)
            )


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
            ind["predicted_ancestry"] = ped_info[ind_id].get(
                "ancestry-prediction", "UNKNOWN"
            )
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
    ind_info["upd_regions_bed"] = sample.get(
        "upd_regions_bed", sample.get("upd_regions_bed")
    )
    ind_info["upd_sites_bed"] = sample.get("upd_sites_bed", sample.get("upd_sites_bed"))
    ind_info["mt_bam"] = sample.get("mt_bam")
    ind_info["analysis_type"] = sample.get("analysis_type")

    # Path to downloadable vcf2cytosure file
    ind_info["vcf2cytosure"] = sample.get("vcf2cytosure")

    # load sma file if it is not done at this point!
    ind_info["is_sma"] = sample.get("is_sma", None)
    ind_info["is_sma_carrier"] = sample.get("is_sma_carrier", None)
    ind_info["smn1_cn"] = sample.get("smn1_cn", None)
    ind_info["smn2_cn"] = sample.get("smn2_cn", None)
    ind_info["smn2delta78_cn"] = sample.get("smn2delta78_cn", None)
    ind_info["smn_27134_cn"] = sample.get("smn_27134_cn", None)

    ind_info["capture_kits"] = (
        [sample.get("capture_kit")] if "capture_kit" in sample else []
    )

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
    return removeNoneRecursive(ind_info)


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
    # create a config object based on pydantic rules
    configObj = ScoutLoadConfig(**config)
    vcf_files = VcfFiles(**config)  # vcf_files parsed separetly
    configObj.vcf_files = vcf_files
    case_data = configObj.dict()  # translate object to dict

    # add SMN info
    LOG.debug("Checking for SMN TSV..")
    if case_data["smn_tsv"]:
        LOG.info("Adding SMN info from {}.".format(case_data["smn_tsv"]))
        add_smn_info_case(case_data)

    return removeNoneRecursive(configObj.dict())


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

    LOG.debug("return (parse_ped): {}".format(family_id))
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


def removeNoneRecursive(dictionary):
    """Recusivly remove None from dictionary"""
    return removeNoneRecursive_aux(dictionary, {})


def removeNoneRecursive_aux(dictionary, new_dict):
    LOG.debug("diction: {}".format(dictionary))
    for key, value in dictionary.items():
        if value is not None:
            new_dict.update({key: value})
        if (
            isinstance(value, list)
            and len(value) > 0
                and key not in ["collaborators", "cohorts", "default_panels", "gene_panels", "capture_kits", "phenotype_terms"]
        ):
            new_list = [removeNoneRecursive_aux(item, {}) for item in value]
            new_dict.update({key: new_list})

    return new_dict
