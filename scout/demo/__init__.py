import importlib_resources

###### Paths ######
# Panel paths
panel_path = importlib_resources.files("scout") / "demo/panel_1.txt"
panelapp_panel_path = importlib_resources.files("scout") / "demo/panelapp_test_panel.json"

# Case paths
ped_path = importlib_resources.files("scout") / "demo/643594.ped"
madeline_path = importlib_resources.files("scout") / "demo/madeline.xml"
load_path = importlib_resources.files("scout") / "demo/643594.config.yaml"
cancer_load_path = importlib_resources.files("scout") / "demo/cancer.load_config.yaml"
rnafusion_load_path = importlib_resources.files("scout") / "demo/rnafusion.load_config.yaml"
delivery_report_path = importlib_resources.files("scout") / "demo/delivery_report.html"
cnv_report_path = importlib_resources.files("scout") / "demo/cancer_cnv_report.pdf"
coverage_qc_report_path = importlib_resources.files("scout") / "demo/cancer_coverage_qc_report.html"
gene_fusion_report_path = importlib_resources.files("scout") / "demo/draw-fusions-example.pdf"

# Variant paths
clinical_snv_path = importlib_resources.files("scout") / "demo/643594.clinical.vcf.gz"
clinical_sv_path = importlib_resources.files("scout") / "demo/643594.clinical.SV.vcf.gz"
clinical_str_path = importlib_resources.files("scout") / "demo/643594.clinical.str.stranger.vcf.gz"
customannotation_snv_path = importlib_resources.files("scout") / "demo/customannotations_one.vcf.gz"
vep_97_annotated_path = (
    importlib_resources.files("scout") / "demo/vep97_annotated_clnsig_conservation_revel.vcf"
)
vep_104_annotated_path = importlib_resources.files("scout") / "demo/vep104_annotated.vcf"
research_snv_path = importlib_resources.files("scout") / "demo/643594.research.vcf.gz"
research_sv_path = importlib_resources.files("scout") / "demo/643594.research.SV.vcf.gz"
cancer_snv_path = importlib_resources.files("scout") / "demo/cancer_test.vcf.gz"
cancer_sv_path = (
    importlib_resources.files("scout") / "demo/manta_vep_94_annotated_sv_cancer_file.vcf.gz"
)
empty_sv_clinical_path = importlib_resources.files("scout") / "demo/empty.clinical.SV.vcf.gz"
