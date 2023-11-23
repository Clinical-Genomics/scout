from importlib_resources import files

BASE_PATH = "scout.demo"

###### Paths ######
# Panel paths
panel_path = str(files(BASE_PATH).joinpath("panel_1.txt"))
panelapp_panel_path = str(files(BASE_PATH).joinpath("panelapp_test_panel.json"))

# Case paths
ped_path = str(files(BASE_PATH).joinpath("643594.ped"))
madeline_path = str(files(BASE_PATH).joinpath("madeline.xml"))
load_path = str(files(BASE_PATH).joinpath("643594.config.yaml"))
cancer_load_path = str(files(BASE_PATH).joinpath("cancer.load_config.yaml"))
rnafusion_load_path = str(files(BASE_PATH).joinpath("rnafusion.load_config.yaml"))
delivery_report_path = str(files(BASE_PATH).joinpath("delivery_report.html"))
cnv_report_path = str(files(BASE_PATH).joinpath("cancer_cnv_report.pdf"))
coverage_qc_report_path = str(files(BASE_PATH).joinpath("cancer_coverage_qc_report.html"))
gene_fusion_report_path = str(files(BASE_PATH).joinpath("draw-fusions-example.pdf"))

# Variant paths
clinical_snv_path = str(files(BASE_PATH).joinpath("643594.clinical.vcf.gz"))
clinical_sv_path = str(files(BASE_PATH).joinpath("643594.clinical.SV.vcf.gz"))
clinical_str_path = str(files(BASE_PATH).joinpath("643594.clinical.str.stranger.vcf.gz"))
clinical_fusion_path = str(files(BASE_PATH).joinpath("fusion_data.vcf"))
customannotation_snv_path = str(files(BASE_PATH).joinpath("customannotations_one.vcf.gz"))
vep_97_annotated_path = str(
    files(BASE_PATH).joinpath("vep97_annotated_clnsig_conservation_revel.vcf")
)
vep_104_annotated_path = str(files(BASE_PATH).joinpath("vep104_annotated.vcf"))
research_snv_path = str(files(BASE_PATH).joinpath("643594.research.vcf.gz"))
research_sv_path = str(files(BASE_PATH).joinpath("643594.research.SV.vcf.gz"))
cancer_snv_path = str(files(BASE_PATH).joinpath("cancer_test.vcf.gz"))
cancer_sv_path = str(files(BASE_PATH).joinpath("manta_vep_94_annotated_sv_cancer_file.vcf.gz"))
empty_sv_clinical_path = str(files(BASE_PATH).joinpath("empty.clinical.SV.vcf.gz"))
