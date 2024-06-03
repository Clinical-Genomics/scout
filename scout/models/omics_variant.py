""" OMICS variant

    For potentially causative variants that are not yet in ClinVar
    and have yet not been marked causative in any existing case.

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from scout.utils.md5 import generate_md5_key


class OmicsVariantLoader(BaseModel):
    # An OmicsVariant on db will also have
    case_id: str
    institute_id: str
    build: str = "38"
    variant_type: str = "clinical"
    category: str = ("outlier",)
    sub_category: str = ("fraser",)
    date: datetime.datetime
    display_name: str

    # omics_variant_id  gene, category, sub_category, qualification
    # display_id
    # omics variant id hash (including clinical/research)

    # DROP Fraser and Outrider outlier TSVs

    # sample id is mandatory: each row pertains to one outlier event in one individual as compared to others
    sampleID: str

    # outlier variants must identify the gene they pertain to, primarily with an hgnc_id
    hgnc_id: Optional[str]
    geneID: Optional[str]
    hgncSymbol: Optional[str] = Field(serialization_alias="hgnc_symbol")
    gene_name_orig: Optional[str]

    gene_type: Optional[str]

    # coordinates if applicable
    seqnames: Optional[str] = Field(serialization_alias="chrom")
    start: Optional[int]
    end: Optional[int]
    width: Optional[int]
    strand: Optional[str]

    pValue: Optional[float]

    # Fraser specific
    type: Optional[str]
    psiValue: Optional[float]
    deltaPsi: Optional[float]
    counts: Optional[int]
    totalCounts: Optional[int]
    meanCounts: Optional[float]
    meanTotalCounts: Optional[float]
    nonsplitCounts: Optional[int]
    nonsplitProportion: Optional[float]
    nonsplitProportion_99quantile: Optional[float]
    annotatedJunction: Optional[str]
    pValueGene: Optional[float]
    padjustGene: Optional[float]
    PAIRED_END: Optional[str]
    isExternal: Optional[bool]
    potentialImpact: Optional[str]
    causesFrameshift: Optional[str]
    UTR_overlap: Optional[str]
    blacklist: Optional[bool]

    # Outrider specific
    padjust: Optional[float]
    zScore: Optional[float]
    l2fc: Optional[float]
    rawcounts: Optional[int]
    normcounts: Optional[float]
    meanCorrected: Optional[float]
    theta: Optional[float]
    aberrant: Optional[bool]
    aberrantBySample: Optional[float]
    aberrantByGene: Optional[float]
    padj_rank: Optional[float]
    FDR_set: Optional[str]
    foldChange: Optional[float]

    @model_validator(mode="before")
    def set_display_name(cls, values) -> "OmicsVariantLoader":
        """Set a free text qualification, depending on the kind of variant."""

        if values.get("sub_category") == "outrider":
            qualification = "up" if zScore > 0 else "down"
        if values.get("sub_category") == "fraser":
            qualification = values.get("potentialImpact")

            values["display_name"] = "_".join(
                [
                    values.get("hgncSymbol"),
                    values.get("category"),
                    values.get("sub_category"),
                    qualification,
                    values.get("seqnames"),  # chrom, unserialised
                    values.get("start"),
                    values.get("end"),
                    values.get("variant_type"),
                ]
            )
        return values

    @model_validator(mode="before")
    def set_omics_variant_id(cls, values) -> "OmicsVariantLoader":
        """Set OMICS variant id based on the kind of variant."""

        if values.get("sub_category") == "outrider":
            qualification = "up" if zScore > 0 else "down"
        if values.get("sub_category") == "fraser":
            qualification = values.get("potentialImpact")

            values["omics_variant_id"] = "_".join(
                [
                    values.get("seqnames"),  # chrom, unserialised
                    values.get("start"),
                    values.get("end"),
                    values.get("build"),
                    values.get("hgncSymbol"),
                    values.get("sub_category"),
                    qualification,
                    values.get("variant_type"),
                ]
            )
        return values

    @model_validator(mode="before")
    def set_display_name(cls, values) -> "OmicsVariantLoader":
        """Set a display name."""
        values["display_name"] = values.get(
            "display_name", values.get("sample_name", values.get("individual_id"))
        )
        return values
