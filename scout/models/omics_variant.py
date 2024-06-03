""" OMICS variant

    For potentially causative variants that are not yet in ClinVar
    and have yet not been marked causative in any existing case.

"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from scout.utils.md5 import generate_md5_key

class OmicsVariantLoader(BaseModel):
    # case_id: str
    # build: str
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
    zScore:  Optional[float]
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




class OmicsVariant(dict):
    """
    # required primary fields
    chromosome=str,  # required
    position=int,  # required
    end=int,  # required
    reference=str,  # required
    alternative=str,  # required
    build=str, # required, ["37","38"], default "37"
    date=datetime.datetime
    # required derived fields
    # display name is variant_id (no md5) chrom_pos_ref_alt (simple_id)
    display_name=str,  # required

    #optional fields
    # maintainer user_id list
    maintainer=list(user_id), # optional
    institute=institute_id, # optional

    # optional fields foreseen for future use
    category=str,  # choices=('sv', 'snv', 'str', 'cancer', 'cancer_sv')
    sub_category=str,  # choices=('snv', 'indel', 'del', 'ins', 'dup', 'inv', 'cnv', 'bnd', 'str')
    description=str,
    """


    def __init__(
        self,
        institute,
        case,
        maintainer=[],
        build="37",
        date=None,
        category="outlier",
        sub_category="splicing",
        description=None,
        variant_type="clinical"
        samples=list,  # list of dictionaries that are <gt_calls>
    ):
        super(OmicsVariant, self).__init__()
        self["chromosome"] = str(chromosome)
        self["position"] = position
        self["end"] = end
        self["build"] = build

        self["reference"] = reference
        self["alternative"] = alternative

        self["omics_variant_id"] = "_".join(
            [
                str(part)
                for part in (
                    chromosome,
                    position,
                    category,
                    sub_category,
                    build,
                )
            ]
        )
        self["display_id"] = "_".join(
            [str(part) for part in (chromosome, position, reference, alternative)]
        )
        self["variant_id"] = generate_md5_key(
            [str(part) for part in (chromosome, position, reference, alternative, "clinical")]
        )
        self["date"] = date or datetime.now()

        self["institute"] = institute or None
        self["maintainer"] = maintainer or []
        self["category"] = category
        self["sub_category"] = sub_category
        self["description"] = description
