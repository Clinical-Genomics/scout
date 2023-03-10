import importlib_resources

BASE_PATH = importlib_resources.files("scout")

###### Paths ######
# Panel paths
panel_path = BASE_PATH / "demo/panel_1.txt"
panelapp_panel_path = BASE_PATH / "demo/panelapp_test_panel.json"

# Case paths
ped_path = BASE_PATH / "demo/643594.ped"
madeline_path = BASE_PATH / "demo/madeline.xml"
load_path = BASE_PATH / "demo/643594.config.yaml"
cancer_load_path = BASE_PATH / "demo/cancer.load_config.yaml"
rnafusion_load_path = BASE_PATH / "demo/rnafusion.load_config.yaml"
delivery_report_path = BASE_PATH / "demo/delivery_report.html"
cnv_report_path = BASE_PATH / "demo/cancer_cnv_report.pdf"
coverage_qc_report_path = str(BASE_PATH / "demo/cancer_coverage_qc_report.html")
gene_fusion_report_path = BASE_PATH / "demo/draw-fusions-example.pdf"

# Variant paths
clinical_snv_path = BASE_PATH / "demo/643594.clinical.vcf.gz"
clinical_sv_path = BASE_PATH / "demo/643594.clinical.SV.vcf.gz"
clinical_str_path = BASE_PATH / "demo/643594.clinical.str.stranger.vcf.gz"
customannotation_snv_path = BASE_PATH / "demo/customannotations_one.vcf.gz"
vep_97_annotated_path = BASE_PATH / "demo/vep97_annotated_clnsig_conservation_revel.vcf"
vep_104_annotated_path = BASE_PATH / "demo/vep104_annotated.vcf"
research_snv_path = BASE_PATH / "demo/643594.research.vcf.gz"
research_sv_path = BASE_PATH / "demo/643594.research.SV.vcf.gz"
cancer_snv_path = BASE_PATH / "demo/cancer_test.vcf.gz"
cancer_sv_path = BASE_PATH / "demo/manta_vep_94_annotated_sv_cancer_file.vcf.gz"
empty_sv_clinical_path = BASE_PATH / "demo/empty.clinical.SV.vcf.gz"
