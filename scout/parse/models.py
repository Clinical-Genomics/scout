"""Class to hold information about scout load config and subclasses used"""

import datetime
import logging
import re
from fractions import Fraction
from glob import glob
from pathlib import Path
from typing import Any, ByteString, Dict, List, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator
from typing_extensions import Literal

from scout.exceptions import ConfigError, PedigreeError
from scout.utils.date import get_date

LOG = logging.getLogger(__name__)

# As the class constructor is called twice, this messes with the
# aliases, removing the set value the second time called. It seems
# to work by adding the aliased name as a attribute...
#
class ChromographImages(BaseModel):
    autozygous: Optional[str] = None
    coverage: Optional[str] = None
    upd_regions: Optional[str] = None
    upd_sites: Optional[str] = None


def _glob_wildcard(path):
    """Search for multiple files using a path with wildcard."""
    wildcard = re.search(r"{([A-Za-z0-9_-]+)}", path)
    # make proper wildcard path
    glob_path = path[: wildcard.start()] + "*" + path[wildcard.end() :]
    wildcard_end = len(path) - wildcard.end()
    paths = tuple(
        {
            "match": match[wildcard.start() : -wildcard_end],
            "variable_name": wildcard.group(1),
            "path": Path(match),
        }
        for match in glob(glob_path)
    )
    return paths


def _replace_wildcard_with_match(match, image):
    path_expanded = image.path.replace("{%s}" % match["variable_name"], match["match"])
    str_repid = match["match"]
    title_expanded = image.title.replace("{%s}" % match["variable_name"], match["match"])

    return Image(
        path=path_expanded,
        description=image.description,
        height=image.height,
        format=image.format,
        width=image.width,
        title=title_expanded,
        str_repid=str_repid,
    )


def is_wildcard(string_path):
    """Return true if string_path contains { and }, used to contruct wildcard matching"""
    return "{" in string_path and "}" in string_path


class Image(BaseModel):
    data: Optional[str] = None
    description: Optional[str] = None
    height: Optional[int] = None
    format: Optional[str] = None
    path: str = None
    str_repid: Optional[str] = None
    title: str = None
    width: Optional[int] = None

    def __eq__(self, other):
        return self.title == other.title


class ScoutIndividual(BaseModel):
    alignment_path: Optional[str] = None
    analysis_type: Literal["wgs", "wes", "mixed", "unknown", "panel", "external"] = None
    bam_file: Optional[str] = ""
    bam_path: Optional[str] = None
    capture_kits: Optional[str] = Field(alias="capture_kit")  #!
    chromograph_images: Optional[ChromographImages] = ChromographImages()
    confirmed_parent: Optional[bool] = None
    confirmed_sex: Optional[bool] = None
    display_name: Optional[str] = None
    father: Optional[str] = None
    individual_id: str = Field(alias="sample_id")
    is_sma: Optional[str] = None
    is_sma_carrier: Optional[str] = None
    mother: Optional[str] = None
    msi: Optional[str] = None
    mt_bam: Optional[str] = None
    phenotype: Literal["affected", "unaffected", "unknown"]
    predicted_ancestry: Optional[str] = None
    rhocall_bed: Optional[str] = None
    rhocall_wig: Optional[str] = None
    rna_coverage_bigwig: Optional[str] = None
    sample_name: Optional[str] = None
    sex: Literal["unknown", "female", "male"]
    smn1_cn: Optional[int] = None
    smn2_cn: Optional[int] = None
    smn2delta78_cn: Optional[int] = None
    smn_27134_cn: Optional[int] = None
    splice_junctions_bed: Optional[str] = None
    tiddit_coverage_wig: Optional[str] = None
    tissue_type: Optional[str] = None
    tmb: Optional[str] = None
    tumor_purity: Optional[float] = 0.0
    tumor_type: Optional[str] = None
    upd_regions_bed: Optional[str] = None
    upd_sites_bed: Optional[str] = None
    vcf2cytosure: Optional[str] = None

    @validator("tumor_purity")
    def cast_tumor_purity_float(cls, value):
        if isinstance(value, str):
            return float(Fraction(value))
        return value

    @validator("capture_kits")
    def cast_capture_kits_string(cls, value):
        if isinstance(value, str):
            return [value]
        return value

    @root_validator
    def update_bam_file(cls, values):
        """Update bam_file to either alignment_path, bam_file or
        bam_path"""
        if values.get("alignment_path"):
            values.update({"bam_file": values.get("alignment_path")})
            return values
        if values.get("bam_file"):
            # Dont't touch anything
            return values
        if values.get("bam_path"):
            values.update({"bam_file": values.get("bam_path")})
            return values
        return values

    @root_validator
    def set_display_name(cls, values):
        """Set display_name to 1. sample_name
        2. sample_id"""
        if values.get("sample_name"):
            values.update({"display_name": values.get("sample_name")})
            return values
        if values.get("individual_id"):
            # Dont't touch anything
            values.update({"display_name": values.get("individual_id")})
            return values
        return values


# VCF Files
class VcfFiles(BaseModel):
    vcf_cancer: Optional[str] = None
    vcf_cancer_research: Optional[str] = None
    vcf_cancer_sv: Optional[str] = None
    vcf_cancer_sv_research: Optional[str] = None
    vcf_snv: Optional[str] = None
    vcf_snv_research: Optional[str] = None
    vcf_str: Optional[str] = None
    vcf_sv: Optional[str] = None
    vcf_sv_research: Optional[str] = None


def update_image_list_on_wildcard(image_list):
    """Traverse a list of Image() objects and expand on wildcards.
    Returns a list of Images."""
    updated_image_list = []
    for image in image_list:
        if is_wildcard(image.path):
            for match in _glob_wildcard(image.path):
                replaced = _replace_wildcard_with_match(match, image)
                updated_image_list.append(replaced)
        else:
            updated_image_list.append(image)
    return updated_image_list


def remove_none_images(image_list):
    VALID_IMAGE_SUFFIXES = ["gif", "svg", "png", "jpg", "jpeg"]
    updated_image_list = []
    for image in image_list:
        LOG.debug("IMAGE:{}".format(image))
        path = Path(image.path)
        if path.suffix[1:] in VALID_IMAGE_SUFFIXES:
            updated_image_list.append(image)
    return updated_image_list


def read_filestream(image_list):
    """"""
    for image in image_list:
        path = Path(image.path)
        with open(path, "rb") as file_handle:
            bytestream = bytes(file_handle.read())
            image.data = bytestream
            image.format = "svg+xml" if path.suffix[1:] == "svg" else path.suffix[1:]


class CustomImage(BaseModel):
    """Top Level Custom Image Config Class

    Note that all image wild cards are expanded by this top-level class, therefore
    reading of binaries and checking correct image formats is done here
    """

    case: Dict[str, List[Image]] = []
    str: List[Image] = []

    @root_validator
    def expand_wildcards(cls, values):
        """Traverse every Image object and exand wildcards."""
        # 1. Travers variant lists and expand wildcards
        variant_list = values["str"]
        values["str"] = update_image_list_on_wildcard(variant_list)

        # 2. Travers case dict and expand wildcards
        cases = values["case"]
        cases_updated = {}
        for entry in cases:
            image_list = cases[entry]
            cases_updated[entry] = update_image_list_on_wildcard(image_list)
        values["case"] = cases_updated
        return values

    @root_validator
    def remove_invalid_files(cls, values):
        """Traverse every Image object and remove non-image files"""
        # 1. Travers variant lists and
        variant_list = values["str"]
        values["str"] = remove_none_images(variant_list)

        # 2. Travers case dict and
        cases = values["case"]

        cases_updated = {}
        for entry in cases:
            image_list = cases[entry]
            cases_updated[entry] = remove_none_images(image_list)
        values["case"] = cases_updated
        return values

    @root_validator
    def read_binaries(cls, values):
        """Read image binaries for all Image entries to store in db"""
        variant_list = values["str"]
        read_filestream(variant_list)

        cases = values["case"]
        for entry in cases:
            image_list = cases[entry]
            read_filestream(image_list)
        return values


class ScoutLoadConfig(BaseModel):
    analysis_date: Any = datetime.datetime.now()
    assignee: Optional[str] = None
    case_id: str = Field(alias="family")
    cnv_report: Optional[str] = None
    cohorts: Optional[List[str]] = None
    collaborators: Optional[List[str]] = None
    coverage_qc_report: Optional[str] = None
    custom_images: Optional[CustomImage] = None

    # -  custom_images: Dict[str, List[Image]] = None
    # custom_images: Dict[str, Dict[str, List[Image]]] = None
    default_panels: Optional[List[str]] = Field([], alias="default_gene_panels")
    delivery_report: Optional[str] = None
    display_name: Optional[str] = Field(alias="family_name")
    family: str = None
    gene_fusion_report: Optional[str] = None
    gene_fusion_report_research: Optional[str] = None
    gene_panels: Optional[List[str]] = []
    genome_build: int = Field([], alias="human_genome_build")
    individuals: List[ScoutIndividual] = Field([], alias="samples")
    lims_id: Optional[str] = None
    madeline_info: Optional[str] = Field("", alias="madeline")  #!
    multiqc: Optional[str] = None
    owner: str = None
    peddy_ped: Optional[str] = None
    peddy_ped_check: Optional[str] = Field("", alias="peddy_check")
    peddy_sex_check: Optional[str] = Field("", alias="peddy_sex")
    phenotype_terms: Optional[List[str]] = None
    rank_model_version: Optional[str] = ""
    rank_score_threshold: Optional[int] = 0
    smn_tsv: Optional[str] = None
    sv_rank_model_version: Optional[str] = ""
    synopsis: Union[List[str], str] = None
    track: Literal["rare", "cancer"] = "rare"
    vcf_files: Optional[VcfFiles]

    def __init__(self, **data):
        """Override init() for handling nested vcf_files dicts.
        Use try/except to handle TypeError if `vcf_files`is already set in
        previous call `parse_case_data()` or `parse_case()`."""
        vcfs = VcfFiles(**data)
        try:
            super().__init__(vcf_files=vcfs, **data)
        except TypeError as err:
            super().__init__(**data)

    @validator("analysis_date")
    def analysis_date_to_Datetime(cls, analysis_date):
        """Check if analysis_date is on datetime format or string convertible to datetime.
        Otherwise return now."""
        if isinstance(analysis_date, datetime.datetime):
            return analysis_date
        try:
            return get_date(analysis_date)
        except ValueError as err:
            LOG.warning("Analysis date is on wrong format: {}".format(err))
            LOG.warning("Setting analysis date to todays date")
            return datetime.datetime.now()

    @validator("owner", pre=True, always=True)
    def mandatory_check_owner(cls, value):
        """`owner` is mandatory in a case configuration. If not
        provided in config file an exception is raised"""
        if value is None:
            raise ConfigError("A case has to have a owner")
        return value

    @validator("family", pre=True, always=True)
    def mandatory_check_family(cls, value):
        """`family` is mandatory in a case configuration. If not
        provided in config file an exception is raised"""
        if value is None:
            raise ConfigError("A case has to have a 'family'")
        return value

    @validator("madeline_info")
    def check_if_madeline_exists(cls, path):
        """Add the pedigree figure, this is a xml file which is
        dumped in the db"""
        mad_path = Path(path)
        try:
            if not mad_path.exists():
                raise ValueError("madeline path not found: {}".format(mad_path))
        except OSError:
            # 2nd time called, catch OSerror and return
            return path
        with mad_path.open("r") as in_handle:
            return in_handle.read()

    @validator("individuals")
    def family_relations_consistent(cls, individuals):
        """Check family relationships. If configured parent exist. If
        individual(s) are configured"""
        individual_dicts = [i.dict() for i in individuals]
        if len(individual_dicts) == 0:
            raise PedigreeError("No samples could be found")
        all_ids = [i["individual_id"] for i in individual_dicts]
        # Check if relations are correct
        for parsed_ind in individual_dicts:
            father = parsed_ind.get("father")
            if father and father != "0":
                if father not in all_ids:
                    raise PedigreeError("father %s does not exist in family" % father)
            mother = parsed_ind.get("mother")
            if mother and mother != "0":
                if mother not in all_ids:
                    raise PedigreeError("mother %s does not exist in family" % mother)
        return individuals

    @validator("synopsis")
    def cast_synopsis_to_string(cls, my_synopsis):
        if isinstance(my_synopsis, list):
            return ". ".join(my_synopsis)
        return my_synopsis

    @root_validator
    def update_track_to_cancer(cls, values):
        """Set track to 'cancer' if certain vcf-files are set"""
        vcfs = values.get("vcf_files")
        try:
            vcf_dict = vcfs.dict()
            if (
                vcf_dict["vcf_cancer"]
                or vcf_dict["vcf_cancer_research"]
                or vcf_dict["vcf_cancer_sv"]
                or vcf_dict["vcf_cancer_sv_research"]
            ):
                values.update({"track": "cancer"})
        except Exception as error:
            LOG.error("exception in vcf_s! Not set? {}".format(error))
        return values

    @root_validator
    def set_collaborators(cls, values):
        """Update collaborators to `owner` if not set"""
        if values.get("collaborators") is None:
            owner = values.get("owner")
            values.update({"collaborators": [owner]})
        return values

    @root_validator
    def set_display_name(cls, values):
        """Set toplevel 'display_name', in prioritised order 1. family_name  2. family"""
        if values.get("display_name") is None:
            values.update({"display_name": values.get("family")})
        return values

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True
