import pkg_resources


###### Files ######

# Gene panel:
panel_file = 'demo/panel_1.txt'

# Case info
load_file = 'demo/643594.config.yaml'
clinical_snv_file = 'demo/643594.clinical.vcf'
research_snv_file = 'demo/643594.research.vcf'

clinical_sv_file = 'demo/643594.clinical.SV.vcf'
research_sv_file = 'demo/643594.research.SV.vcf'

panel_path = pkg_resources.resource_filename('scout', panel_file)
load_path = pkg_resources.resource_filename('scout', load_file)

clinical_snv_path = pkg_resources.resource_filename('scout', clinical_snv_file)
clinical_sv_path = pkg_resources.resource_filename('scout', clinical_sv_file)

research_snv_path = pkg_resources.resource_filename('scout', research_snv_file)
research_sv_path = pkg_resources.resource_filename('scout', research_sv_file)