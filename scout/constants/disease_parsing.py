import re

MIMNR_PATTERN = re.compile("[0-9]{6,6}")
ENTRY_PATTERN = re.compile("\([1,2,3,4]\)")

DISEASE_INHERITANCE_TERMS = [
    "Autosomal recessive",
    "Autosomal dominant",
    "Digenic recessive",
    "X-linked dominant",
    "X-linked recessive",
    "Y-linked",
    "Mitochondrial",
    "Mitochondrial inheritance",
]

INHERITANCE_TERMS_MAPPER = {
    "Autosomal recessive": "AR",
    "Autosomal dominant": "AD",
    "Digenic recessive": "DR",
    "X-linked dominant": "XD",
    "X-linked recessive": "XR",
    "Y-linked": "Y",
    "Mitochondrial": "MT",
    "Mitochondrial inheritance": "MT",
}

OMIM_STATUS_MAP = {"[": "nondisease", "{": "susceptibility", "?": "provisional"}
