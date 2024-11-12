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
                            "documentation": 'Strength can be modified based on <a href="https://pubmed.ncbi.nlm.nih.gov/30192042/" rel="noopener noreferrer" target="_blank">Tayoun et al</a> and <a href="http://autopvs1.genetics.bgi.com/" rel="noopener noreferrer" target="_blank">AutoPVS1</a>, or for RNA <a href="https://www.clinicalgenome.org/docs/application-of-the-acmg-amp-framework-to-capture-evidence-relevant-to-predicted-and-observed-impact-on-splicing-recommendations/" target="_blank">Walker et al</a>.',
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
                            "short": "Known pathogenic aa",
                            "description": "Same amino acid change as a previously established pathogenic variant regardless of nucleotide change",
                        },
                    ),
                    (
                        "PS2",
                        {
                            "short": "<i>De novo</i> (confirmed)",
                            "description": "De novo (both maternity and paternity confirmed) in a patient with the disease and no family history",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/site/assets/files/3461/svi_proposal_for_de_novo_criteria_v1_1.pdf" rel="noopener noreferrer" target="_blank">SVI <i>de novo</i></a>.',
                        },
                    ),
                    (
                        "PS3",
                        {
                            "short": "Functional damage",
                            "description": "Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product, and the evidence is strong",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/docs/recommendations-for-application-of-the-functional-evidence-ps3-bs3-criterion-using-the-acmg-amp-sequence-variant-interpretation/" rel="noopener noreferrer" target="_blank">Brnich 2019</a>.',
                        },
                    ),
                    (
                        "PS4",
                        {
                            "short": "In >=4 unrelated patients, not controls",
                            "description": "The prevalence of the variant in affected individuals is significantly increased compared with the prevalence in controls; 4 or more unrelated patients",
                            "documentation": '<a href="https://www.acgs.uk.com/media/11631/uk-practice-guidelines-for-variant-classification-v4-01-2020.pdf" rel="noopener noreferrer" target="_blank">ACGS (Ellard et al 2020)</a> suggest <a href="https://www.medcalc.org/calc/odds_ratio.php" target="_blank">Odds ratio calculator</a>, '
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
                            "documentation": 'Apply only if variant is expected to be detected in large population datasets - see e.g. <a href="https://pubmed.ncbi.nlm.nih.gov/31479589/" rel="noopener noreferrer" target="_blank">Harrison et al 2019</a>.',
                        },
                    ),
                    (
                        "PM3",
                        {
                            "short": "In trans pathogenic & AR",
                            "description": "For recessive disorders, detected in trans with a pathogenic variant",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/site/assets/files/3717/svi_proposal_for_pm3_criterion_-_version_1.pdf" rel="noopener noreferrer" target="_blank">SVI in <i>trans</i></a>.',
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
                            "short": "Similar to known pathogenic aa",
                            "description": "Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before, the amino acids have similar properties and the evidence is strong",
                        },
                    ),
                    (
                        "PM6",
                        {
                            "short": "<i>De novo</i> (unconfirmed)",
                            "description": "Assumed de novo, but without confirmation of paternity and maternity",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/site/assets/files/3461/svi_proposal_for_de_novo_criteria_v1_1.pdf" rel="noopener noreferrer" target="_blank">SVI <i>de novo</i></a>.',
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
                            "short": "Cosegregation",
                            "description": "Cosegregation with disease in multiple affected family members in a gene definitively known to cause the disease, and the evidence is weak",
                            "documentation": 'Strength can be modified <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4908147/" target="_blank" rel="noopener noreferrer">Jarvik 2016</a>, <a href="https://clinicalgenome.org/docs/clingen-guidance-for-use-of-the-pp1-bs4-co-segregation-and-pp4-phenotype-specificity-criteria-for-sequence-variant/" rel="noopener noreferrer" target="_blank">Biesecker et al 2023</a>',
                        },
                    ),
                    (
                        "PP2",
                        {
                            "short": "Missense: important",
                            "description": "Missense variant in a gene that has a low rate of benign missense variation and in which missense variants are a common mechanism of disease",
                        },
                    ),
                    (
                        "PP3",
                        {
                            "short": "Predicted pathogenic",
                            "description": "Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc)",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/docs/calibration-of-computational-tools-for-missense-variant-pathogenicity-classification-and-clingen-recommendations-for-pp3-bp4-cri/" rel="noopener noreferrer" target="_blank">Pejaver et al</a>',
                        },
                    ),
                    (
                        "PP4",
                        {
                            "short": "Phenotype: single gene",
                            "description": "Patient's phenotype or family history is highly specific for a disease with a single genetic etiology",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/docs/clingen-guidance-for-use-of-the-pp1-bs4-co-segregation-and-pp4-phenotype-specificity-criteria-for-sequence-variant/" target="_blank" rel="noopener noreferrer">Biesecker et al 2023</a>',
                        },
                    ),
                    (
                        "PP5",
                        {
                            "short": "Reported pathogenic, evidence unavailable",
                            "description": "Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation",
                            "documentation": 'Deprecated by ClinGen SVI <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6709533/" target="_blank" rel="noopener noreferrer">Biesecker et al 2018</a>.',
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
                            "short": "Frequency >=0.05",
                            "description": "Allele frequency is >=0.05 in a general continental population dataset",
                            "documentation": 'For clarification and exceptions see <a href="https://clinicalgenome.org/docs/updated-recommendation-for-the-benign-stand-alone-acmg-amp-criterion/" target="_blank" rel="noopener noreferrer">Ghosh et al</a>',
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
                            "short": "No functional damage",
                            "description": "Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing, and the evidence is strong",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/docs/recommendations-for-application-of-the-functional-evidence-ps3-bs3-criterion-using-the-acmg-amp-sequence-variant-interpretation/" rel="noopener noreferrer" target="_blank">Brnich 2019</a>.',
                        },
                    ),
                    (
                        "BS4",
                        {
                            "short": "Non-segregation",
                            "description": "Lack of segregation in affected members of a family, and the evidence is strong",
                            "documentation": 'Strength can be modified based on <a href="https://clinicalgenome.org/docs/clingen-guidance-for-use-of-the-pp1-bs4-co-segregation-and-pp4-phenotype-specificity-criteria-for-sequence-variant/" target="_blank" rel="noopener noreferrer">Biesecker et al 2023</a>',
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
                            "documentation": 'Deprecated by ClinGen SVI <a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6709533/" rel="noopener noreferrer" target="_blank">Biesecker et al</a>.',
                        },
                    ),
                    (
                        "BP7",
                        {
                            "short": "Synonymous, no impact on splicing",
                            "description": "A synonymous variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site",
                        },
                    ),
                ]
            ),
        ),
    ]
)

ACMG_POTENTIAL_CONFLICTS = [
    (
        "PVS1",
        "PM4",
        "Use of PVS1 and PM4 together risks double-counting evidence (Tayoun et al 2019).",
    ),
    (
        "PVS1",
        "PM1",
        "Use of PVS1 and PM1 together is not recommended (Durkie et al 2024).",
    ),
    (
        "PVS1",
        "PP2",
        "Use of PVS1 and PP2 together is not recommended (Durkie et al 2024).",
    ),
    (
        "PVS1",
        "PS3",
        "Note that for RNA PS3 should only be taken with PVS1 for well established functional assays, not splicing alone (Walker 2023).",
    ),
    (
        "PS1",
        "PM4",
        "Use of PS1 and PM4 together is not recommended (Durkie et al 2024).",
    ),
    (
        "PS1",
        "PM5",
        "Use of PS1 and PM5 together conflicts with original definition (Richards et al 2015).",
    ),
    (
        "PS1",
        "PP3",
        "Use of PS1 and PP3 together risks double-counting evidence (Tayoun et al 2019).",
    ),
    (
        "PS2",
        "PM6",
        "Use of PS2 and PM6 together conflicts with original definition (Richards et al 2015).",
    ),
    (
        "PM1",
        "PP2",
        "Avoid double-counting evidence for constraints in both PM1 and PP2 (Durkie et al 2024).",
    ),
]
