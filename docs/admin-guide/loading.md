#Loading Scout

When loading a case into scout it is possible to use either a config file or to specify parameters on the command line.

## Scout Load Config

The loading config is a `.yaml` file and can include all the necessary information to scout. Command line options will overload information in the config file.

The config file has the following specification:

```yaml
owner: str(mandatory)

family: str(mandatory)
samples:
  - analysis_type: str(optional), [wgs,wes]
    sample_id: str(mandatory)
    capture_kit: str(optional)
    father: str(mandatory)
    mother: str(mandatory)
    sample_name: str(mandatory)
    phenotype: str(mandatory), [affected, unaffected, unknown]
    sex: str(mandatory), [male, female, unknown]
    expected_coverage: int(mandatory)

vcf_snv: str(optional)
vcf_sv: str(optional)
vcf_cancer: str(optional)
vcf_snv_research: str(optional)
vcf_sv_research: str(optional)
vcf_cancer_research: str(optional)

madeline: str(optional)
default_gene_panels: list[str](optional)
gene_panels: list[str](optional)

# meta data
rank_model_version: float(optional)
rank_score_threshold: float(optional)
analysis_date: datetime(optional)
human_genome_build: str(optional)
```

An example file, (this file is located in `scout/demo/643594.config.yaml`):

```yaml
---

owner: cust000

family: '643594'
samples:
  - analysis_type: wes
    sample_id: ADM1059A2
    capture_kit: Agilent_SureSelectCRE.V1
    father: ADM1059A1
    mother: ADM1059A3
    sample_name: NA12882
    phenotype: affected
    sex: male
    expected_coverage: 30
  - analysis_type: wes
    sample_id: ADM1059A1
    capture_kit: Agilent_SureSelectCRE.V1
    father: '0'
    mother: '0'
    sample_name: NA12877
    phenotype: unaffected
    sex: male
    expected_coverage: 30
  - analysis_type: wes
    sample_id: ADM1059A3
    capture_kit: Agilent_SureSelectCRE.V1
    father: '0'
    mother: '0'
    sample_name: NA12878
    phenotype: unaffected
    sex: female
    expected_coverage: 30

vcf_snv: scout/demo/643594.clinical.vcf.gz
vcf_sv: scout/demo/643594.clinical.SV.vcf.gz
vcf_snv_research: scout/demo/643594.research.vcf.gz
vcf_sv_research: scout/demo/643594.research.SV.vcf.gz

madeline: scout/demo/madeline.xml
default_gene_panels: [panel1]
gene_panels: [panel1]

# meta data
rank_model_version: 1.12
rank_score_threshold: -100
analysis_date: 2016-10-12 14:00:46
human_genome_build: 37

```

## Load case from CLI without config

Cases can be loaded without config file, in that case the user needs to specify a ped file and optionally one or several VCF files. An example could look like

```
scout load case --ped path/to/file.ped --vcf-snv path/to/file.vcf
```

Please use 

```
scout load case --help
```

for more instructions