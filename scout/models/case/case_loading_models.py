import logging
import re
from datetime import datetime
from enum import Enum
from fractions import Fraction
from glob import glob
from os.path import abspath, dirname, exists, isabs
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from scout.constants import ANALYSIS_TYPES, FILE_TYPE_MAP, OMICS_FILE_TYPE_MAP
from scout.exceptions import PedigreeError
from scout.utils.date import get_date

LOG = logging.getLogger(__name__)
REPID = "{REPID}"

SAMPLES_FILE_PATH_CHECKS = [
    "bam_file",
    "d4_file",
    "mitodel_file",
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

CASE_FILE_PATH_CHECKS = [
    "cnv_report",
    "coverage_qc_report",
    "delivery_report",
    "exe_ver",
    "fraser_tsv",
    "gene_fusion_report",
    "gene_fusion_report_research",
    "madeline_info",
    "multiqc",
    "multiqc_rna",
    "outrider_tsv",
    "peddy_ped",
    "peddy_ped_check",
    "peddy_sex_check",
    "smn_tsv",
    "reference_info",
    "RNAfusion_inspector",
    "RNAfusion_inspector_research",
    "RNAfusion_report",
    "RNAfusion_report_research",
]

VCF_FILE_PATH_CHECKS = FILE_TYPE_MAP.keys()
OMICS_FILE_PATH_CHECKS = OMICS_FILE_TYPE_MAP.keys()

GENOME_BUILDS = ["37", "38"]
TRACKS = ["rare", "cancer"]
SUPPORTED_IMAGE_FORMATS = ["gif", "svg", "png", "jpg", "jpeg"]


class PhenoType(str, Enum):
    affected = "affected"
    unaffected = "unaffected"


class Sex(str, Enum):
    male = "male"
    female = "female"
    unknown = "unknown"


def _resource_abs_path(string_path: str) -> str:
    """Return the absolute path to a resource file."""
    if not exists(string_path):
        raise FileExistsError(f"Path {string_path} could not be found on disk.")
    if isabs(string_path):
        return string_path
    return abspath(string_path)


#### VCF files class ####


class VcfFiles(BaseModel):
    """A class representing any type of VCF file."""

    vcf_cancer: Optional[str] = None
    vcf_cancer_research: Optional[str] = None
    vcf_cancer_sv: Optional[str] = None
    vcf_cancer_sv_research: Optional[str] = None
    vcf_snv: Optional[str] = None
    vcf_snv_mt: Optional[str] = None
    vcf_snv_research: Optional[str] = None
    vcf_snv_research_mt: Optional[str] = None
    vcf_mei: Optional[str] = None
    vcf_mei_research: Optional[str] = None
    vcf_str: Optional[str] = None
    vcf_sv: Optional[str] = None
    vcf_sv_mt: Optional[str] = None
    vcf_sv_research: Optional[str] = None
    vcf_sv_research_mt: Optional[str] = None
    vcf_fusion: Optional[str] = None
    vcf_fusion_research: Optional[str] = None

    @model_validator(mode="before")
    def validate_file_path(cls, values: Dict) -> "VcfFiles":
        """Make sure that VCF file exists on disk."""
        for item in VCF_FILE_PATH_CHECKS:
            item_path: str = values.get(item)
            if item_path:
                values[item] = _resource_abs_path(item_path)
        return values


#### Samples - related pydantic models ####


class BioNanoAccess(BaseModel):
    project: Optional[str] = None
    sample: Optional[str] = None


class ChromographImages(BaseModel):
    autozygous: Optional[str] = None
    coverage: Optional[str] = None
    upd_regions: Optional[str] = None
    upd_sites: Optional[str] = None

    @model_validator(mode="before")
    def validate_file_path(cls, config_values: Dict) -> "SampleLoader":
        """Make sure that chromograph paths associated to samples exist on disk and are absolute paths. Chromograph paths are incomplete paths, containing the path to the directory containing a number of files plus the prefix of the files."""

        for key in cls.model_fields:
            item_path: str = config_values.get(key)
            if item_path:
                item_path_dirname: str = dirname(item_path)
                config_values[key] = item_path.replace(
                    item_path_dirname, _resource_abs_path(item_path_dirname)
                )
        return config_values


class Mitodel(BaseModel):
    discordant: Optional[int] = None
    normal: Optional[int] = None
    ratioppk: Optional[float] = None


class OmicsFiles(BaseModel):
    """Represents multiple kinds of omics files, e.g. RNA expression outliers for aberrant splicing
    and aberrant expression."""

    fraser: Optional[str] = None
    fraser_research: Optional[str] = None
    outrider: Optional[str] = None
    outrider_research: Optional[str] = None

    @model_validator(mode="before")
    def validate_file_path(cls, values: Dict) -> "OmicsFiles":
        """Make sure that VCF file exists on disk."""
        for item in OMICS_FILE_PATH_CHECKS:
            item_path: str = values.get(item)
            if item_path:
                values[item] = _resource_abs_path(item_path)
        return values


class REViewer(BaseModel):
    alignment: Optional[str] = None
    alignment_index: Optional[str] = None
    vcf: Optional[str] = None
    catalog: Optional[str] = None
    reference: Optional[str] = None
    reference_index: Optional[str] = None

    @model_validator(mode="before")
    def validate_file_path(cls, config_values: Dict) -> "SampleLoader":
        """Make sure that REViewer paths associated to samples exist on disk and are absolute paths."""
        for key in cls.model_fields:
            item_path: str = config_values.get(key)
            if item_path:
                config_values[key] = _resource_abs_path(item_path)
        return config_values


class SampleLoader(BaseModel):
    alignment_path: Optional[str] = None
    analysis_type: Literal[ANALYSIS_TYPES] = None
    bam_file: Optional[str] = ""
    bam_path: Optional[str] = None
    bionano_access: Optional[BioNanoAccess] = None
    capture_kits: Optional[Union[str, List]] = Field(None, alias="capture_kit")
    chromograph_images: Optional[ChromographImages] = ChromographImages()
    confirmed_parent: Optional[bool] = None
    confirmed_sex: Optional[bool] = None
    d4_file: Optional[str] = None
    display_name: Optional[str] = None
    father: Optional[str] = None
    individual_id: str = Field(alias="sample_id")
    is_sma: Optional[str] = None
    is_sma_carrier: Optional[str] = None
    mitodel_file: Optional[str] = None
    mitodel: Optional[Mitodel] = Mitodel()
    mother: Optional[str] = None
    msi: Optional[str] = None
    mt_bam: Optional[str] = None
    phenotype: Literal["affected", "unaffected", "unknown"]
    predicted_ancestry: Optional[str] = None
    reviewer: Optional[REViewer] = REViewer()
    rhocall_bed: Optional[str] = None
    rhocall_wig: Optional[str] = None
    rna_alignment_path: Optional[str] = None
    rna_coverage_bigwig: Optional[str] = None
    omics_sample_id: Optional[str] = None
    sample_name: Optional[str] = None
    sex: Literal["unknown", "female", "male"]
    smn1_cn: Optional[int] = None
    smn2_cn: Optional[int] = None
    smn2delta78_cn: Optional[int] = None
    smn_27134_cn: Optional[int] = None
    splice_junctions_bed: Optional[str] = None
    subject_id: Optional[str] = None
    tiddit_coverage_wig: Optional[str] = None
    tissue_type: Optional[str] = None
    tmb: Optional[str] = None
    tumor_purity: Optional[float] = 0.0
    tumor_type: Optional[str] = None
    upd_regions_bed: Optional[str] = None
    upd_sites_bed: Optional[str] = None
    vcf2cytosure: Optional[str] = None

    class Config:
        populate_by_name = True

    @model_validator(mode="before")
    def convert_cancer_int_values_to_str(cls, values) -> "SampleLoader":
        """Sets 'msi' and 'msi' values for cancer cases to string. This is a required step in Pydantic2, in Pydantic1 values were just coerced from int to str."""
        for item in ["msi", "tmb"]:
            if values.get(item):
                values[item] = str(values[item])
        return values

    @field_validator("tumor_purity", mode="before")
    @classmethod
    def set_tumor_purity(cls, tumor_purity: Union[str, float]) -> float:
        """Set tumor purity value as a fraction."""
        if isinstance(tumor_purity, str):
            return float(Fraction(tumor_purity))
        return tumor_purity

    @model_validator(mode="before")
    def set_sample_display_name(cls, values) -> "SampleLoader":
        """Make sure a sample as a display name."""
        values["display_name"] = values.get(
            "display_name", values.get("sample_name", values.get("individual_id"))
        )
        return values

    @model_validator(mode="before")
    def set_alignment_path(cls, values) -> "SampleLoader":
        """prefer key 'bam file over 'alignment_path' or 'bam_path'."""
        values["bam_file"] = values.get(
            "alignment_path", values.get("bam_file", values.get("bam_path"))
        )
        return values

    @model_validator(mode="before")
    def validate_file_path(cls, values: Dict) -> "SampleLoader":
        """Make sure that files associated to samples (mostly alignment files) exist on disk."""
        for item in SAMPLES_FILE_PATH_CHECKS:
            item_path: str = values.get(item)
            if item_path:
                values[item] = _resource_abs_path(item_path)
        return values

    @field_validator("capture_kits", mode="before")
    @classmethod
    def set_capture_kits(cls, capture_kits: Optional[Union[str, List[str]]]) -> Optional[List]:
        """Format capture kit (str) as a list of items."""
        if isinstance(capture_kits, str):
            return [capture_kits]
        return capture_kits


#### Custom images - related classes ####


class Image(BaseModel):
    """A class representing an image either associated to a case or a str variant."""

    description: Optional[str] = None
    height: Optional[int] = None
    format: Optional[str] = None
    path: Optional[str] = None
    str_repid: Optional[str] = None
    title: Optional[str] = None
    width: Optional[int] = None

    @field_validator("path", mode="before")
    @classmethod
    def check_image_path(cls, path: str) -> Optional[str]:
        """Make sure that the image is has standard format."""
        image_format: str = path.split(".")[-1]
        if image_format not in SUPPORTED_IMAGE_FORMATS:
            raise TypeError(
                f"Custom images should be of type: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            )
        if REPID not in path and exists(path) is False:
            raise ValueError(f"Image path '{path}' is not valid.")

        return path


def set_custom_images(images: Optional[List[Image]]) -> Optional[List[Image]]:
    """Fix custom image's path and data."""

    if images is None:
        return

    def _glob_wildcard(path) -> Tuple[Dict]:
        """Search for multiple files using a path with wildcard."""
        wildcard = re.search(r"{([A-Za-z0-9_-]+)}", path)
        # make proper wildcard path
        glob_path = path[: wildcard.start()] + "*" + path[wildcard.end() :]
        wildcard_end = len(path) - wildcard.end()
        matches = tuple(
            {
                "repid": match[wildcard.start() : -wildcard_end],
                "path": Path(match),
            }
            for match in glob(glob_path)
        )
        return matches

    real_folder_images: List[Image] = []
    for image in images:
        if image.str_repid == REPID:  # This will be more than one image in a folder
            for match in _glob_wildcard(path=image.path):
                new_image: Dict = {
                    "description": image.description.replace(REPID, match["repid"]),
                    "height": image.height,
                    "format": None,
                    "path": _resource_abs_path(str(match["path"])),
                    "str_repid": match["repid"],
                    "title": image.title.replace(REPID, match["repid"]),
                    "width": image.width,
                }
                real_folder_images.append(Image(**new_image))
        else:
            image.path = _resource_abs_path(image.path)
            real_folder_images.append(image)  # append other non-repid images

    return real_folder_images


class RawCustomImages(BaseModel):
    """This class makes a preliminary check that custom_images in the load config file has the expected structure for the custom images.."""

    str_variants_images: Optional[List[Image]] = []
    case_images: Optional[Dict[str, List[Image]]] = {}

    @model_validator(mode="before")
    def set_custom_image(cls, values: Dict) -> "RawCustomImages":
        values["str_variants_images"] = values.get(
            "str_variants_images",
            values.get("str"),
        )
        values["case_images"] = values.get(
            "case_images",
            values.get("case"),
        )
        return values


class ParsedCustomImages(BaseModel):
    """This class corresponds to the parsed fields of the custom_images config item."""

    str_variants_images: Optional[List[Image]] = []
    case_images: Optional[Dict[str, List[Image]]] = {}


#### Case - related pydantic models ####


class CaseLoader(BaseModel):
    analysis_date: Optional[Any] = datetime.now()
    assignee: Optional[str] = None
    case_id: str = Field(alias="family")
    cnv_report: Optional[str] = None
    cohorts: Optional[List[str]] = None
    collaborators: Optional[List[str]] = None
    coverage_qc_report: Optional[str] = None
    custom_images: Optional[Union[RawCustomImages, ParsedCustomImages]] = None
    default_panels: Optional[List[str]] = Field([], alias="default_gene_panels")
    delivery_report: Optional[str] = None
    display_name: Optional[str] = Field(None, alias="family_name")
    exe_ver: Optional[str] = None
    family: Optional[str] = None
    gene_fusion_report: Optional[str] = None
    gene_fusion_report_research: Optional[str] = None
    gene_panels: Optional[List[str]] = []
    genome_build: str
    rna_genome_build: Optional[str] = "38"
    individuals: Union[List[SampleLoader]] = Field([], alias="samples")
    lims_id: Optional[str] = None
    madeline_info: Optional[str] = Field(None, alias="madeline")
    multiqc: Optional[str] = None
    multiqc_rna: Optional[str] = None
    omics_files: Optional[OmicsFiles] = None
    owner: Optional[str] = None
    peddy_ped: Optional[str] = None  # Soon to be deprecated
    peddy_ped_check: Optional[str] = Field(None, alias="peddy_check")  # Soon to be deprecated
    peddy_sex_check: Optional[str] = Field(None, alias="peddy_sex")  # Soon to be deprecated
    phenotype_groups: Optional[List[str]] = None
    phenotype_terms: Optional[List[str]] = None
    exe_ver: Optional[str] = None
    rank_model_version: Optional[str] = None
    rank_score_threshold: Optional[int] = 0
    reference_info: Optional[str] = None
    RNAfusion_inspector: Optional[str] = None
    RNAfusion_inspector_research: Optional[str] = None
    RNAfusion_report: Optional[str] = None
    RNAfusion_report_research: Optional[str] = None
    smn_tsv: Optional[str] = None
    sv_rank_model_version: Optional[str] = None
    synopsis: Optional[Union[List[str], str]] = None
    track: Literal["rare", "cancer"] = "rare"
    vcf_files: Optional[VcfFiles]

    def __init__(self, **data):
        """Override init() for handling nested vcf_files dicts.
        Use try/except to handle TypeError if `vcf_files`is already set in
        previous call `parse_case_data()` or `parse_case()`."""
        vcfs = VcfFiles(**data)
        try:
            super().__init__(vcf_files=vcfs, **data)
        except TypeError:
            super().__init__(**data)

    @model_validator(mode="before")
    def set_case_id(cls, values) -> "CaseLoader":
        """Make sure case will have an _id."""
        values.update({"case_id": values.get("case_id", values.get("family"))})
        return values

    @model_validator(mode="before")
    def set_gene_panels(cls, values) -> "CaseLoader":
        """Make sure gene_panels and default_gene_panels doesn't contain strings with spaces."""
        for panels_type in ["default_default_panels", "default_panels", "gene_panels"]:
            if not values.get(panels_type):
                continue
            values[panels_type] = [panel.strip() for panel in values[panels_type]]

        if values.get("default_panels"):
            values["default_default_panels"] = values["default_panels"]

        return values

    @field_validator("analysis_date", mode="before")
    @classmethod
    def set_analysis_date(cls, analysis_date: Optional[Any]) -> datetime:
        """Make sure analysis date is set."""
        if isinstance(analysis_date, datetime):
            return analysis_date
        try:
            return get_date(analysis_date)
        except ValueError:
            LOG.warning(
                "An error occurred while formatting the analysis date. Setting it to today's date."
            )
            return datetime.now()

    @field_validator("madeline_info", mode="after")
    def check_if_madeline_exists(cls, madeline: str) -> Optional[str]:
        """Add the pedigree figure."""
        madeline_path = Path(madeline)
        try:
            with madeline_path.open("r") as in_handle:
                return in_handle.read()
        except Exception as ex:
            LOG.warning(f"madeline_info is not reachable or a valid path: {ex}.")

    @field_validator("synopsis", mode="before")
    @classmethod
    def set_synopsis(cls, synopsis: Optional[Union[str, List]]) -> Optional[str]:
        """Make sure that synopsis will be saved as a string even if it's passed as a list of strings."""
        if isinstance(synopsis, List):
            synopsis = ". ".join(synopsis)
        return synopsis

    @model_validator(mode="before")
    @classmethod
    def format_build(cls, values) -> "CaseLoader":
        """Format the RNA genome build collected from RNA_human_genome_build key."""
        rna_str_build = str(values.get("rna_human_genome_build", "38"))
        values["rna_genome_build"] = _get_str_build(rna_str_build)
        return values

    @model_validator(mode="before")
    @classmethod
    def format_rna_build(cls, values) -> "CaseLoader":
        """Format the genome build collected from genome_build or human_genome_build keys."""
        dna_str_build = str(values.get("genome_build") or values.get("human_genome_build", ""))
        values["genome_build"] = _get_str_build(dna_str_build)
        return values

    @field_validator("individuals", mode="after")
    @classmethod
    def check_family_relations_consistent(
        cls, individuals: List[SampleLoader]
    ) -> List[SampleLoader]:
        """Check family relationships. If configured parent exist. If
        individual(s) are configured."""
        if not individuals:
            raise PedigreeError("No samples could be found")

        individual_dicts = [i.model_dump() for i in individuals]
        all_ids = [i["individual_id"] for i in individual_dicts]
        # Check if relations are correct
        for parsed_ind in individual_dicts:
            father = parsed_ind.get("father")
            if father and father != "0" and father not in all_ids:
                raise PedigreeError("father %s does not exist in family" % father)
            mother = parsed_ind.get("mother")
            if mother and mother != "0" and mother not in all_ids:
                raise PedigreeError("mother %s does not exist in family" % mother)
        return individuals

    @model_validator(mode="before")
    def validate_file_path(cls, values: Dict) -> "CaseLoader":
        """Make sure the files associated to the case (mostly reports) exist on disk."""
        for item in CASE_FILE_PATH_CHECKS:
            item_path: str = values.get(item)
            if item_path:
                values[item] = _resource_abs_path(item_path)

        return values

    @field_validator("custom_images", mode="after")
    @classmethod
    def parse_custom_images(cls, custom_images: RawCustomImages) -> ParsedCustomImages:
        """Fixes image path and image data for each custom image in variant_custom_images and case_images."""

        custom_images.str_variants_images = set_custom_images(
            images=custom_images.str_variants_images
        )

        for key, images in custom_images.case_images.items():
            custom_images.case_images[key] = set_custom_images(
                images=custom_images.case_images[key]
            )

        return custom_images

    @model_validator(mode="before")
    def set_collaborators(cls, values) -> "CaseLoader":
        """Set collaborators to owner if no collaborators are provided."""
        if values.get("collaborators") is None:
            owner = values.get("owner")
            if owner is None:
                raise ValueError("Case owner is missing.")
            values["collaborators"] = [values["owner"]]
        return values


def _get_str_build(str_build):
    """Get genome build, as either '37' or '38'."""
    if "37" in str_build:
        str_build = "37"
    elif "38" in str_build:
        str_build = "38"
    if str_build not in GENOME_BUILDS:
        raise ValueError("Genome build must be either '37' or '38'.")
    return str_build
