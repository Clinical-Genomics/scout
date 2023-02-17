# -*- coding: utf-8 -*-
from collections import OrderedDict

# from worst to most certain benign
ACMG_MAP = OrderedDict(
    [
        (4, "pathogenic"),
        (3, "likely_pathogenic"),
        (0, "uncertain_significance"),
        (2, "likely_benign"),
        (1, "benign"),
    ]
)

REV_ACMG_MAP = OrderedDict([(value, key) for key, value in ACMG_MAP.items()])

ACMG_OPTIONS = [
    {"code": "pathogenic", "short": "P", "label": "Pathogenic", "color": "danger"},
    {
        "code": "likely_pathogenic",
        "short": "LP",
        "label": "Likely Pathogenic",
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

ACMG_COMPLETE_MAP = OrderedDict([(option["code"], option) for option in ACMG_OPTIONS])

ACMG_CRITERIA = OrderedDict()

ACMG_CRITERIA["pathogenicity"] = OrderedDict(
    [
        (
            "Very Strong",
            OrderedDict(
                [
                    (
                        "PVS1",
                        {
                            "short": "Null variant",
                            "description": "Null variant (nonsense, frameshift, canonical +/- 2 bp splice sites, initiation codon, single or multiexon deletion) in a gene where LOF is a known mechanism of disease.",
                            "documentation": 'Strength can be modified based on <a href="https://pubmed.ncbi.nlm.nih.gov/30192042/" target="_blank">Tayoun et al</a> and <a href="http://autopvs1.genetics.bgi.com/" target="_blank">AutoPVS1</a>.',
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
                        "PS1",
                        {
                            "short": "Known pathogenic aa (HQ)",
                            "description": "Same amino acid change as a previously established pathogenic variant regardless of nucleotide change",
                        },
                    ),
                    (
                        "PS2",
                        {
                            "short": "De novo (confirmed)",
                            "description": "De novo (both maternity and paternity confirmed) in a patient with the disease and no family history",
                        },
                    ),
                    (
                        "PS3",
                        {
                            "short": "Functional damage (HQ)",
                            "description": "Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product, and the evidence is strong",
                        },
                    ),
                    (
                        "PS4",
                        {
                            "short": "In >=4 unrelated patients, not controls",
                            "description": "The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls; 4 or more unrelated patients",
                            "documentation": '<a href="https://www.acgs.uk.com/media/11631/uk-practice-guidelines-for-variant-classification-v4-01-2020.pdf" target="_blank">ACGS (Ellard et al 2020)</a> suggest <a href="https://www.medcalc.org/calc/odds_ratio.php" target="_blank">Odds ratio calculator</a>, '
                            "and application with strength modification for fewer unrelated affected individuals or gnomAD controls.",
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
                        "PM1",
                        {
                            "short": "Functional domain",
                            "description": "Located in a mutational hot spot and/or critical and well-established functional domain  (e.g., active site of an enzyme) without benign variation",
                        },
                    ),
                    (
                        "PM2",
                        {
                            "short": "Not in matched controls",
                            "description": "Absent from controls (or at extremely low frequency if recessive), in ethnically matched population",
                            "documentation": 'Apply only if variant is expected to be detected in large population datasets - see e.g. <a href="https://pubmed.ncbi.nlm.nih.gov/31479589/" target="_blank">Harrison et al 2019</a>.',
                        },
                    ),
                    (
                        "PM3",
                        {
                            "short": "In trans pathogenic & AR",
                            "description": "For recessive disorders, detected in trans with a pathogenic variant.",
                        },
                    ),
                    (
                        "PM4",
                        {
                            "short": "In-frame/stop-loss; moderate impact",
                            "description": "Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss variants.",
                        },
                    ),
                    (
                        "PM5",
                        {
                            "short": "Similar to known pathogenic aa (HQ)",
                            "description": "Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before,  the amino acids have similar properties and the evidence is strong",
                        },
                    ),
                    (
                        "PM6",
                        {
                            "short": "De novo (unconfirmed)",
                            "description": "Assumed de novo, but without confirmation of paternity and maternity",
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
                        "PP1",
                        {
                            "short": "Cosegregation (WQ)",
                            "description": "Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease, and the evidence is weak",
                        },
                    ),
                    (
                        "PP2",
                        {
                            "short": "Missense: important",
                            "description": "Missense variant in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease.",
                        },
                    ),
                    (
                        "PP3",
                        {
                            "short": "Predicted pathogenic",
                            "description": "Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc.)",
                        },
                    ),
                    (
                        "PP4",
                        {
                            "short": "Phenotype: single gene",
                            "description": "Patient's phenotype or family history is highly specific for a disease with a single genetic etiology",
                        },
                    ),
                    (
                        "PP5",
                        {
                            "short": "Reported pathogenic, evidence unavailable",
                            "description": "Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation",
                        },
                    ),
                ]
            ),
        ),
    ]
)

ACMG_CRITERIA["benign impact"] = OrderedDict(
    [
        (
            "Stand-alone",
            OrderedDict(
                [
                    (
                        "BA1",
                        {
                            "short": "Frequency >=hi_freq_cutoff",
                            "description": "Allele frequency is >=hi_freq_cutoff in ESP, 1000G or ExAC",
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
                        "BS1",
                        {
                            "short": "Frequency >expected & AD",
                            "description": "Allele frequency is greater than expected for disorder, and the inheritance is autosomal dominant.",
                        },
                    ),
                    (
                        "BS2",
                        {
                            "short": "In documented healthy",
                            "description": "Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder, with full penentrance expected at an early age",
                        },
                    ),
                    (
                        "BS3",
                        {
                            "short": "No functional damage (HQ)",
                            "description": "Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing, and the evidence is strong",
                        },
                    ),
                    (
                        "BS4",
                        {
                            "short": "Non-segregation (HQ)",
                            "description": "Lack of segregation in affected members of a family, and the evidence is strong",
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
                        "BP1",
                        {
                            "short": "Missense; not important",
                            "description": "Missense variant in a gene for which primarily truncating variants are known to cause disease",
                        },
                    ),
                    (
                        "BP2",
                        {
                            "short": "In trans & AD, or in cis pathogenic",
                            "description": "Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or in cis with a pathogenic variant in any inheritance pattern",
                        },
                    ),
                    (
                        "BP3",
                        {
                            "short": "In-frame; non-functional",
                            "description": "In-frame insertions/delitions in a repetitive region without a known function",
                        },
                    ),
                    (
                        "BP4",
                        {
                            "short": "Predicted benign",
                            "description": "Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, evolutionary, splicing impact, etc.)",
                        },
                    ),
                    (
                        "BP5",
                        {
                            "short": "Other causative variant found",
                            "description": "Variant found in a case with an alternate molecular basis for disease",
                        },
                    ),
                    (
                        "BP6",
                        {
                            "short": "Reported benign, evidence unavailable",
                            "description": "Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an independent evaluation",
                        },
                    ),
                    (
                        "BP7",
                        {
                            "short": "(not in use)",
                            "description": "A synonymous variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site",
                        },
                    ),
                ]
            ),
        ),
    ]
)
