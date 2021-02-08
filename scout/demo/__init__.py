import pkg_resources

###### Files ######
# Gene panel:
panel_file = "demo/panel_1.txt"
madeline_file = "demo/madeline.xml"

# Case info
ped_file = "demo/643594.ped"
load_file = "demo/643594.config.yaml"
cancer_load_file = "demo/cancer.load_config.yaml"

clinical_snv_file = "demo/643594.clinical.vcf.gz"
research_snv_file = "demo/643594.research.vcf.gz"
customannotation_snv_file = "demo/customannotations_one.vcf.gz"
vep_97_annotated_snv_file = "demo/vep97_annotated_clnsig_conservation_revel.vcf"
manta_annotated_sv_cancer_file = "demo/manta_vep_94_annotated_sv_cancer_file.vcf.gz"
cancer_snv_file = "demo/cancer_test.vcf.gz"

ped_path = pkg_resources.resource_filename("scout", ped_file)
clinical_sv_file = "demo/643594.clinical.SV.vcf.gz"
research_sv_file = "demo/643594.research.SV.vcf.gz"
empty_sv_file = "demo/empty.clinical.SV.vcf.gz"

clinical_str_file = "demo/643594.clinical.str.stranger.vcf.gz"

panel_path = pkg_resources.resource_filename("scout", panel_file)
madeline_path = pkg_resources.resource_filename("scout", madeline_file)
load_path = pkg_resources.resource_filename("scout", load_file)
cancer_load_path = pkg_resources.resource_filename("scout", cancer_load_file)

clinical_snv_path = pkg_resources.resource_filename("scout", clinical_snv_file)
clinical_sv_path = pkg_resources.resource_filename("scout", clinical_sv_file)
clinical_str_path = pkg_resources.resource_filename("scout", clinical_str_file)

customannotation_snv_path = pkg_resources.resource_filename("scout", customannotation_snv_file)
vep_97_annotated_path = pkg_resources.resource_filename("scout", vep_97_annotated_snv_file)

research_snv_path = pkg_resources.resource_filename("scout", research_snv_file)
research_sv_path = pkg_resources.resource_filename("scout", research_sv_file)

cancer_snv_path = pkg_resources.resource_filename("scout", cancer_snv_file)
cancer_sv_path = pkg_resources.resource_filename("scout", manta_annotated_sv_cancer_file)

empty_sv_clinical_path = pkg_resources.resource_filename("scout", empty_sv_file)

delivery_report_file = "demo/delivery_report.html"
delivery_report_path = pkg_resources.resource_filename("scout", delivery_report_file)

cnv_report_file = "demo/cancer_cnv_report.pdf"
cnv_report_path = pkg_resources.resource_filename("scout", cnv_report_file)
coverage_qc_report_file = "demo/cancer_coverage_qc_report.html"
coverage_qc_report_path = pkg_resources.resource_filename("scout", coverage_qc_report_file)
