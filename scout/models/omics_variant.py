""" OMICS variant

    For potentially causative variants that are not yet in ClinVar
    and have yet not been marked causative in any existing case.

"""

import logging
from datetime import datetime
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, Field, field_validator, model_validator

LOG = logging.getLogger(__name__)


class OmicsVariantLoader(BaseModel):
    """Omics variants loader
    OmicsVariants are e.g. RNA expression outliers as identified by the DROP pipeline.

    Variable names are as found in the original files, plus a set common to all mixed in after file parsing,
    but before model validation by this class.

    The serialisation names will be used when dumping the model for e.g. db storage.
    """

    case_id: str
    institute: str
    build: str = "38"
    variant_type: str = "clinical"
    category: str  # eg "outlier"
    sub_category: str  # eg "splicing"
    date: datetime = datetime.now()
    display_name: str
    omics_variant_id: str

    # DROP Fraser and Outrider outlier TSVs

    # sample id is mandatory: each row pertains to one outlier event in one individual as compared to others
    # In the db object, this will be replaced with a "samples" array of individual dict.
    sample_id: str = Field(
        alias=AliasChoices("sample_id", "sampleID"), serialization_alias="sample_id"
    )

    # outlier variants must identify the gene they pertain to, primarily with an hgnc_id
    hgnc_ids: Optional[List[int]] = Field(alias="hgncId", serialization_alias="hgnc_ids")
    ensembl_gene_id: Optional[str] = Field(
        alias="geneID", serialization_alias="ensembl_gene_id", default=None
    )

    hgnc_symbols: Optional[List[str]] = Field(
        alias="hgncSymbol", serialization_alias="hgnc_symbols"
    )
    gene_name_orig: Optional[str] = Field(
        alias=AliasChoices("geneNameOrig", "gene_name_orig"),
        serialization_alias="gene_name_orig",
        default=None,
    )

    gene_type: Optional[str] = Field(
        alias=AliasChoices("gene_type", "geneType"), serialization_alias="gene_type", default=None
    )

    # coordinates if applicable
    chromosome: Optional[str] = Field(alias="seqnames", serialization_alias="chromosome")
    position: Optional[int] = Field(alias="start", serialization_alias="position")
    end: Optional[int]
    width: Optional[int] = None
    strand: Optional[str] = None

    p_value: Optional[float] = Field(alias="pValue", serialization_alias="p_value", default=None)

    # Fraser specific
    type: Optional[str] = None
    psi_value: Optional[float] = Field(
        alias="psiValue", serialization_alias="psi_value", default=None
    )
    delta_psi: Optional[float] = Field(
        alias="deltaPsi", serialization_alias="delta_psi", default=None
    )
    counts: Optional[int] = None
    total_counts: Optional[int] = Field(
        alias="totalCounts", serialization_alias="total_counts", default=None
    )
    mean_counts: Optional[float] = Field(
        alias="meanCounts", serialization_alias="mean_counts", default=None
    )
    mean_total_counts: Optional[float] = Field(
        alias="meanTotalCounts", serialization_alias="mean_total_counts", default=None
    )
    nonsplit_counts: Optional[int] = Field(
        alias="nonsplitCounts", serialization_alias="nonsplit_counts", default=None
    )
    nonsplit_proportion: Optional[float] = Field(
        alias="nonsplitProportion", serialization_alias="nonsplit_proportion", default=None
    )
    nonsplit_proportion_99quantile: Optional[float] = Field(
        alias="nonsplitproportion99quantile",
        serialization_alias="nonsplit_proportion_99quantile",
        default=None,
    )
    annotated_junction: Optional[str] = Field(
        alias="annotatedJunction", serialization_alias="annotated_junction", default=None
    )
    p_value_gene: Optional[float] = Field(
        alias="pValueGene", serialization_alias="p_value_gene", default=None
    )
    p_adjust_gene: Optional[float] = Field(
        alias="padjustGene", serialization_alias="p_adjust_gene", default=None
    )
    paired_end: Optional[str] = Field(
        alias="pairedEnd", serialization_alias="paired_end", default=None
    )
    is_external: Optional[bool] = Field(
        alias="isExternal", serialization_alias="is_external", default=None
    )
    potential_impact: Optional[str] = Field(
        alias="potentialImpact", serialization_alias="potential_impact", default=None
    )
    causes_frameshift: Optional[str] = Field(
        alias="causesFrameshift", serialization_alias="causes_frameshift", default=None
    )
    utr_overlap: Optional[str] = Field(
        alias="utrOverlap", serialization_alias="utr_overlap", default=None
    )

    # Outrider specific
    padjust: Optional[float] = None
    zscore: Optional[float] = Field(alias="zScore", serialization_alias="zscore", default=None)
    l2fc: Optional[float] = None
    raw_counts: Optional[int] = Field(
        alias="rawcounts", serialization_alias="raw_counts", default=None
    )
    norm_counts: Optional[float] = Field(
        alias="normcounts", serialization_alias="norm_counts", default=None
    )
    mean_corrected: Optional[float] = Field(
        alias="meanCorrected", serialization_alias="mean_corrected", default=None
    )
    theta: Optional[float] = None
    aberrant: Optional[bool] = None
    aberrant_by_sample: Optional[float] = Field(
        alias="aberrantBySample", serialization_alias="aberrant_by_sample", default=None
    )
    aberrant_by_gene: Optional[float] = Field(
        alias="aberrantByGene", serialization_alias="aberrant_by_gene", default=None
    )
    padj_rank: Optional[float] = None
    fdr_set: Optional[str] = Field(alias="FDR_set", serialization_alias="fdr_set", default=None)
    fold_change: Optional[float] = Field(
        alias="foldChange", serialization_alias="fold_change", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, values):
        if isinstance(values, dict):
            return {k: (None if v == "" else v) for k, v in values.items()}
        return values

    @field_validator("chromosome")
    def strip_chr(cls, chrom: str) -> str:
        """We store chromosome names without a chr prefix internally."""
        return chrom.lstrip("chr")

    @model_validator(mode="before")
    def ensure_end(cls, values):
        """End is not always set, but sometimes width is.
        Sometimes Imp is given as end. Worst case we default to width 1."""
        end_guess = int(values.get("start")) + int(values.get("width", 1))
        if "end" not in values:
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

        if "hgncId" in values:
            values["hgncId"] = [int(values.get("hgncId"))]
        elif "hgnc_id" in values:
            values["hgncId"] = [int(values.get("hgnc_id"))]

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
