import pkg_resources


###### Files ######

# Gene panel:
panel_file = 'demo/panel_1.txt'
madeline_file = 'demo/madeline.xml'

# Case info
ped_file = 'demo/643594.ped'
load_file = 'demo/643594.config.yaml'
clinical_snv_file = 'demo/643594.clinical.vcf.gz'
research_snv_file = 'demo/643594.research.vcf.gz'

ped_path = pkg_resources.resource_filename('scout', ped_file)
clinical_sv_file = 'demo/643594.clinical.SV.vcf.gz'
research_sv_file = 'demo/643594.research.SV.vcf.gz'

panel_path = pkg_resources.resource_filename('scout', panel_file)
madeline_path = pkg_resources.resource_filename('scout', madeline_file)
load_path = pkg_resources.resource_filename('scout', load_file)

clinical_snv_path = pkg_resources.resource_filename('scout', clinical_snv_file)
clinical_sv_path = pkg_resources.resource_filename('scout', clinical_sv_file)

research_snv_path = pkg_resources.resource_filename('scout', research_snv_file)
research_sv_path = pkg_resources.resource_filename('scout', research_sv_file)