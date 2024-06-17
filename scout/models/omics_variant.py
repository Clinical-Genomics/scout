""" OMICS variant

    For potentially causative variants that are not yet in ClinVar
    and have yet not been marked causative in any existing case.

"""

import logging
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

LOG = logging.getLogger(__name__)


class OmicsVariantLoader(BaseModel):
    """Omics variants loader
    OmicsVariants are e.g. RNA expression outliers as identified by the DROP pipeline.

    Variable names are as found in the original files, plus a set common to all mixed in after file parsing,
    but before model validation by this class.

    The serialisation names will be used when dumping the model for e.g. db storage.
    """

    case_id: str
    institute_id: str
    build: str = "38"
    variant_type: str = "clinical"
    category: str = "outlier"
    sub_category: str = "splicing"
    date: datetime = datetime.now()
    display_name: str
    omics_variant_id: str
    # omics variant id hash (including clinical/research)?

    # DROP Fraser and Outrider outlier TSVs

    # sample id is mandatory: each row pertains to one outlier event in one individual as compared to others
    sampleID: str

    # outlier variants must identify the gene they pertain to, primarily with an hgnc_id
    hgnc_id: Optional[List[int]] = Field(serialization_alias="hgnc_ids")
    geneID: Optional[str]

    hgncSymbol: Optional[List[str]] = Field(serialization_alias="hgnc_symbols")
    gene_name_orig: Optional[str]

    gene_type: Optional[str]

    # coordinates if applicable
    seqnames: Optional[str] = Field(serialization_alias="chrom")
    start: Optional[int]
    end: Optional[int]
    width: Optional[int] = None
    strand: Optional[str] = None

    pValue: Optional[float]

    # Fraser specific
    type: Optional[str] = None
    psiValue: Optional[float] = None
    deltaPsi: Optional[float] = None
    counts: Optional[int] = None
    totalCounts: Optional[int] = None
    meanCounts: Optional[float] = None
    meanTotalCounts: Optional[float] = None
    nonsplitCounts: Optional[int] = None
    nonsplitProportion: Optional[float] = None
    nonsplitProportion_99quantile: Optional[float] = None
    annotatedJunction: Optional[str] = None
    pValueGene: Optional[float] = None
    padjustGene: Optional[float] = None
    PAIRED_END: Optional[str] = None
    isExternal: Optional[bool] = None
    potentialImpact: Optional[str] = None
    causesFrameshift: Optional[str] = None
    UTR_overlap: Optional[str] = None
    blacklist: Optional[bool] = None

    # Outrider specific
    padjust: Optional[float] = None
    zScore: Optional[float] = None
    l2fc: Optional[float] = None
    rawcounts: Optional[int] = None
    normcounts: Optional[float] = None
    meanCorrected: Optional[float] = None
    theta: Optional[float] = None
    aberrant: Optional[bool] = None
    aberrantBySample: Optional[float] = None
    aberrantByGene: Optional[float] = None
    padj_rank: Optional[float] = None
    FDR_set: Optional[str] = None
    foldChange: Optional[float] = None

    @model_validator(mode="before")
    def ensure_end(cls, values):
        end_guess = int(values.get("start")) + int(values.get("width", 1))
        if not "end" in values:
            values["end"] = end_guess

        if isinstance(values["end"], str):
            if values["end"].isdigit():
                values["end"] = int(values["end"])
            if values["end"] == "Imp":
                # imprecise?
                values["end"] = end_guess

        return values

    @model_validator(mode="before")
    def genes_become_lists(cls, values):
        """HGNC ids and gene symbols are found one on each line in DROP tsvs.
        Convert to a list with a single member in omics_variants for storage."""

        if "hgnc_id" in values:
            values["hgnc_id"] = [int(values.get("hgnc_id"))]

        if "hgncSymbol" in values:
            values["hgncSymbol"] = [str(values.get("hgncSymbol"))]

        return values

    @model_validator(mode="before")
    def set_display_name(cls, values) -> "OmicsVariantLoader":
        """Set a free text qualification, depending on the kind of variant."""

        values["display_name"] = "_".join(
            [
                values.get("hgncSymbol"),
                values.get("category"),
                values.get("sub_category"),
                get_qualification(values=values),
                values.get("seqnames"),  # chrom, unserialised
                str(values.get("start")),
                str(values.get("end")),
                values.get("variant_type"),
            ]
        )
        return values

    @model_validator(mode="before")
    def set_omics_variant_id(cls, values) -> "OmicsVariantLoader":
        """Set OMICS variant id based on the kind of variant."""

        values["omics_variant_id"] = "_".join(
            [
                values.get("seqnames"),  # chrom, unserialised
                str(values.get("start")),
                str(values.get("end")),
                values.get("build"),
                values.get("hgncSymbol"),
                values.get("sub_category"),
                get_qualification(values=values),
                values.get("variant_type"),
            ]
        )
        return values

    @model_validator(mode="before")
    def set_sample_display_name(cls, values) -> "OmicsVariantLoader":
        """Set a display name."""
        values["display_name"] = values.get(
            "display_name", values.get("sample_name", values.get("individual_id"))
        )
        return values


def get_qualification(values: dict) -> str:
    """Get qualification string for ID and display name.
    This string further qualifies the kind of omics event,
    e.g. for an expression outlier it could be 'up' or 'down'."""
    qualification = "affected"
    if values.get("sub_category") == "expression":
        qualification = "up" if float(values.get("zScore", 0)) > 0 else "down"
    if values.get("sub_category") == "splicing":
        qualification = values.get("potentialImpact")
    return qualification
