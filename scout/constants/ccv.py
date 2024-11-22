# -*- coding: utf-8 -*-
from collections import OrderedDict

# from worst to most certain benign
CCV_MAP = OrderedDict(
    [
        (4, "oncogenic"),
        (3, "likely_oncogenic"),
        (0, "uncertain_significance"),
        (2, "likely_benign"),
        (1, "benign"),
    ]
)
# <a href="https://cancerhotspots.org" target="_blank">cancerhotspots.org</a>
REV_CCV_MAP = OrderedDict([(value, key) for key, value in CCV_MAP.items()])

CCV_OPTIONS = [
    {"code": "oncogenic", "short": "O", "label": "Oncogenic", "color": "danger"},
    {
        "code": "likely_oncogenic",
        "short": "LO",
        "label": "Likely Oncogenic",
        "color": "warning",
    },
    {
        "code": "uncertain_significance",
        "short": "VUS",
        "label": "Uncertain Significance",
        "color": "primary",
    },
    {"code": "likely_benign", "short": "LB", "label": "Likely Benign", "color": "info"},
    {"code": "benign", "short": "B", "label": "Benign", "color": "success"},
]

CCV_COMPLETE_MAP = OrderedDict([(option["code"], option) for option in CCV_OPTIONS])

CCV_CRITERIA = OrderedDict()

CCV_CRITERIA["oncogenicity"] = OrderedDict(
    [
        (
            "Very Strong",
            OrderedDict(
                [
                    (
                        "OVS1",
                        {
                            "short": "Null variant in tumor supressor",
                            "description": "Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single-exon or multiexon deletion) in a bona fide tumor suppressor gene.",
                            "documentation": 'Strength can be modified based on <a href="https://pubmed.ncbi.nlm.nih.gov/30192042/" target="blank">ClinGen’s recommendations for PVS1</a>',
                        },
                    )
                ]
            ),
        ),
        (
            "Strong",
            OrderedDict(
                [
                    (
                        "OS1",
                        {
                            "short": "Same aa change as known oncogenic variant",
                            "description": "Same amino acid change as a previously established oncogenic variant (using this standard) regardless of nucleotide change.",
                        },
                    ),
                    (
                        "OS2",
                        {
                            "short": "Well-established functional studies",
                            "description": "Well-established in vitro or in vivo functional studies, supportive of an oncogenic effect of the variant.",
                        },
                    ),
                    (
                        "OS3",
                        {
                            "short": "Cancer hotspot: high frequency",
                            "description": "Located in one of the hotspots in cancerhotspots.org with at least 50 samples with a somatic variant at the same amino acid position, and the same amino acid change count in cancerhotspots.org in at least 10 samples.",
                        },
                    ),
                ]
            ),
        ),
        (
            "Moderate",
            OrderedDict(
                [
                    (
                        "OM1",
                        {
                            "short": "Functional domain",
                            "description": "Located in a critical and well-established part of a functional domain (eg, active site of an enzyme).",
                        },
                    ),
                    (
                        "OM2",
                        {
                            "short": "Protein length change",
                            "description": "Protein length changes as a result of in-frame deletions/insertions in a known oncogene or tumor suppressor gene or stop-loss variants in a known tumor suppressor gene.",
                        },
                    ),
                    (
                        "OM3",
                        {
                            "short": "Cancer hotspot: moderate frequency",
                            "description": "Located in one of the hotspots in cancerhotspots.org with <50 samples with a somatic variant at the same amino acid position, and the same amino acid change count in cancerhotspots.org is at least 10.",
                        },
                    ),
                    (
                        "OM4",
                        {
                            "short": "Missense variant at aa with other oncogenic missense variant",
                            "description": "Missense variant at an amino acid residue where a different missense variant determined to be oncogenic (using this standard) has been documented. Amino acid difference from reference amino acid should be greater or at least approximately the same as for missense change determined to be oncogenic.",
                        },
                    ),
                ]
            ),
        ),
        (
            "Supporting",
            OrderedDict(
                [
                    (
                        "OP1",
                        {
                            "short": "Computatinal evidence",
                            "description": "All used lines of computational evidence support an oncogenic effect of a variant (conservation/evolutionary, splicing effect, etc.).",
                        },
                    ),
                    (
                        "OP2",
                        {
                            "short": "Gene in a malignancy with a single genetic etiology",
                            "description": "Somatic variant in a gene in a malignancy with a single genetic etiology. Example: retinoblastoma is caused by bi-allelic RB1 inactivation.",
                        },
                    ),
                    (
                        "OP3",
                        {
                            "short": "Cancer hotspots: low frequency",
                            "description": "Located in one of the hotspots in cancerhotspots.org and the particular amino acid change count in cancerhotspots.org is below 10",
                        },
                    ),
                    (
                        "OP4",
                        {
                            "short": "Absent in population databases",
                            "description": "Absent from controls (or at an extremely low frequency) in gnomAD.",
                        },
                    ),
                ]
            ),
        ),
    ]
)

CCV_CRITERIA["benign impact"] = OrderedDict(
    [
        (
            "Very Strong",
            OrderedDict(
                [
                    (
                        "SBVS1",
                        {
                            "short": "MAF is >0.05",
                            "description": "Minor allele frequency is >5%% in gnomAD in any 5 general continental populations: African, East Asian, European (non-Finnish), Latino, and South Asian.",
                        },
                    )
                ]
            ),
        ),
        (
            "Strong",
            OrderedDict(
                [
                    (
                        "SBS1",
                        {
                            "short": "MAF is >0.01",
                            "description": "Minor allele frequency is >1%% in gnomAD in any 5 general continental populations: African, East Asian, European (non-Finnish), Latino, and South Asian.	",
                        },
                    ),
                    (
                        "SBS2",
                        {
                            "short": "Well-established functional studies",
                            "description": "Well-established in vitro or in vivo functional studies show no oncogenic effects.",
                        },
                    ),
                ]
            ),
        ),
        (
            "Supporting",
            OrderedDict(
                [
                    (
                        "SBP1",
                        {
                            "short": "Computational evidence",
                            "description": "All used lines of computational evidence suggest no effect of a variant (conservation/evolutionary, splicing effect, etc.).",
                        },
                    ),
                    (
                        "SBP2",
                        {
                            "short": "Silent mutation (no predicted impact on splicing)",
                            "description": "A synonymous (silent) variant for which splicing prediction algorithms predict no effect on the splice consensus sequence nor the creation of a new splice site and the nucleotide is not highly conserved.",
                        },
                    ),
                ]
            ),
        ),
    ]
)

CCV_POTENTIAL_CONFLICTS = [
    (
        "OS2",
        "OS1",
        "If OS1 is applicable, OS2 can be used only if functional studies are based on the particular nucleotide change of the variant.",
    ),
    (
        "OS3",
        "OS1",
        "OS3 cannot be used if OS1 is applicable, unless it is possible to observe hotspots on the basis of the particular nucleotide change.",
    ),
    (
        "OM1",
        "OVS1",
        "OM1 cannot be used if OVS1 is applicable.",
    ),
    (
        "OM3",
        "OM1",
        "OM3 cannot be used if OM1 is applicable.",
    ),
    (
        "OM3",
        "OM4",
        "OM3 cannot be used if OM4 is applicable.",
    ),
]
