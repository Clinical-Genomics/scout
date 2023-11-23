# Collect general information about the file types used in Scout

FILE_TYPE_MAP = {
    "vcf_cancer": {"category": "cancer", "variant_type": "clinical"},
    "vcf_cancer_sv": {"category": "cancer_sv", "variant_type": "clinical"},
    "vcf_cancer_research": {"category": "cancer", "variant_type": "research"},
    "vcf_cancer_sv_research": {"category": "cancer_sv", "variant_type": "research"},
    "vcf_fusion": {"category": "fusion", "variant_type": "clinical"},
    "vcf_fusion_research": {"category": "fusion", "variant_type": "research"},
    "vcf_snv": {"category": "snv", "variant_type": "clinical"},
    "vcf_snv_research": {"category": "snv", "variant_type": "research"},
    "vcf_sv": {"category": "sv", "variant_type": "clinical"},
    "vcf_sv_research": {"category": "sv", "variant_type": "research"},
    "vcf_str": {"category": "str", "variant_type": "clinical"},
    "vcf_mei": {"category": "mei", "variant_type": "clinical"},
    "vcf_mei_research": {"category": "mei", "variant_type": "research"},
}
