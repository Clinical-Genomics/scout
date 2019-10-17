#Loading Scout

## Institute

To load a institute into scout use the command `scout load institute`. As mentioned in the user guide an [institute](../user-guide/institutes.md) has to have a unique internal id, this is specified on the command line with `-i/--internal-id`. Also a display name could be used if there is a need for that, specify with `-d/--display-name`. If no display name is choosen it will default to internal id.
Note that internal id is unique.

## User

To load a user into scout use the command `scout load user`. A user has to:

- belong to an *institute*
- have a *name*
- have a *email adress*

An example could look like:

```bash
scout load user --institute-id cust000 --user-name "Clark Kent" --user-mail clark@mail.com
```


## Case
When loading a case into scout it is possible to use either a config file or to specify parameters on the command line.

### Scout Load Config

The loading config is a `.yaml` file and can include all the necessary information to scout. Command line options will overload information in the config file. For a complete spec of the config file see [load config](load-config.md)

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
    bam_path: path/to/bam
    expected_coverage: 30
  - analysis_type: wes
    sample_id: ADM1059A1
    capture_kit: Agilent_SureSelectCRE.V1
    father: '0'
    mother: '0'
    sample_name: NA12877
    phenotype: unaffected
    sex: male
    bam_path: path/to/bam
    expected_coverage: 30
  - analysis_type: wes
    sample_id: ADM1059A3
    capture_kit: Agilent_SureSelectCRE.V1
    father: '0'
    mother: '0'
    sample_name: NA12878
    phenotype: unaffected
    sex: female
    bam_path: path/to/bam
    expected_coverage: 30

vcf_snv: scout/demo/643594.clinical.vcf.gz
vcf_sv: scout/demo/643594.clinical.SV.vcf.gz
vcf_snv_research: scout/demo/643594.research.vcf.gz
vcf_sv_research: scout/demo/643594.research.SV.vcf.gz

madeline: scout/demo/madeline.xml
default_gene_panels: [panel1]
gene_panels: [panel1]

# meta data
rank_model_version: '1.12'
sv_rank_model_version: '1.5'
rank_score_threshold: -100
analysis_date: 2016-10-12 14:00:46
human_genome_build: 37

```

### Load case from CLI without config

Cases can be loaded without config file, in that case the user needs to specify a ped file and optionally one or several VCF files. An example could look like

```
scout load case --ped path/to/file.ped --vcf-snv path/to/file.vcf
```

Please use

```
scout load case --help
```

for more instructions
