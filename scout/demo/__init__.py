from contextlib import ExitStack

import importlib_resources

file_manager = ExitStack()

file_manager.enter_context(importlib_resources.as_file(EXONS_37))

###### Files ######
# Panel files
panel_file = importlib_resources.files("scout") / "demo/panel_1.txt"
panelapp_file = importlib_resources.files("scout") / "demo/panelapp_test_panel.json"

# Case files
madeline_file = importlib_resources.files("scout") / "demo/madeline.xml"
ped_file = importlib_resources.files("scout") / "demo/643594.ped"
load_file = importlib_resources.files("scout") / "demo/643594.config.yaml"
cancer_load_file = importlib_resources.files("scout") / "demo/cancer.load_config.yaml"
rnafusion_load_file = importlib_resources.files("scout") / "demo/rnafusion.load_config.yaml"
delivery_report_file = importlib_resources.files("scout") / "demo/delivery_report.html"
cnv_report_file = importlib_resources.files("scout") / "demo/cancer_cnv_report.pdf"
coverage_qc_report_file = importlib_resources.files("scout") / "demo/cancer_coverage_qc_report.html"
gene_fusion_report_file = importlib_resources.files("scout") / "demo/draw-fusions-example.pdf"

# Variant files
clinical_snv_file = importlib_resources.files("scout") / "demo/643594.clinical.vcf.gz"
research_snv_file = importlib_resources.files("scout") / "demo/643594.research.vcf.gz"
customannotation_snv_file = importlib_resources.files("scout") / "demo/customannotations_one.vcf.gz"
vep_97_annotated_snv_file = (
    importlib_resources.files("scout") / "demo/vep97_annotated_clnsig_conservation_revel.vcf"
)
vep_104_annotated_snv_file = importlib_resources.files("scout") / "demo/vep104_annotated.vcf"
manta_annotated_sv_cancer_file = (
    importlib_resources.files("scout") / "demo/manta_vep_94_annotated_sv_cancer_file.vcf.gz"
)
cancer_snv_file = importlib_resources.files("scout") / "demo/cancer_test.vcf.gz"
clinical_sv_file = importlib_resources.files("scout") / "demo/643594.clinical.SV.vcf.gz"
research_sv_file = importlib_resources.files("scout") / "demo/643594.research.SV.vcf.gz"
empty_sv_file = importlib_resources.files("scout") / "demo/empty.clinical.SV.vcf.gz"
clinical_str_file = importlib_resources.files("scout") / "demo/643594.clinical.str.stranger.vcf.gz"

###### Paths ######
# Panel paths
panel_path = file_manager.enter_context(importlib_resources.as_file(panel_file))
panelapp_panel_path = file_manager.enter_context(importlib_resources.as_file(panelapp_file))

# Case paths
ped_path = file_manager.enter_context(importlib_resources.as_file(ped_file))
madeline_path = file_manager.enter_context(importlib_resources.as_file(madeline_file))
load_path = file_manager.enter_context(importlib_resources.as_file(load_file))
cancer_load_path = file_manager.enter_context(importlib_resources.as_file(cancer_load_file))
rnafusion_load_path = file_manager.enter_context(importlib_resources.as_file(rnafusion_load_file))
delivery_report_path = file_manager.enter_context(importlib_resources.as_file(delivery_report_file))
cnv_report_path = file_manager.enter_context(importlib_resources.as_file(cnv_report_file))
coverage_qc_report_path = file_manager.enter_context(
    importlib_resources.as_file(coverage_qc_report_file)
)
gene_fusion_report_path = file_manager.enter_context(
    importlib_resources.as_file(gene_fusion_report_file)
)

# Variant paths
clinical_snv_path = file_manager.enter_context(importlib_resources.as_file(clinical_snv_file))
clinical_sv_path = file_manager.enter_context(importlib_resources.as_file(clinical_sv_file))
clinical_str_path = file_manager.enter_context(importlib_resources.as_file(clinical_str_file))
customannotation_snv_path = file_manager.enter_context(
    importlib_resources.as_file(customannotation_snv_file)
)
vep_97_annotated_path = file_manager.enter_context(
    importlib_resources.as_file(vep_97_annotated_snv_file)
)
vep_104_annotated_path = file_manager.enter_context(
    importlib_resources.as_file(vep_104_annotated_snv_file)
)
research_snv_path = file_manager.enter_context(importlib_resources.as_file(research_snv_file))
research_sv_path = file_manager.enter_context(importlib_resources.as_file(research_sv_file))
cancer_snv_path = file_manager.enter_context(importlib_resources.as_file(cancer_snv_file))
cancer_sv_path = file_manager.enter_context(
    importlib_resources.as_file(manta_annotated_sv_cancer_file)
)
empty_sv_clinical_path = file_manager.enter_context(importlib_resources.as_file(empty_sv_file))
