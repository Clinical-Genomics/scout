# The load config

Scout have the possibility to store loads of information about a case and the samples that are included. It is cumbersome to specify to many parameters on the command line so there is an option to give this information in a yaml formated config file.
Here we can give scout some meta information about the analysis, how it was performed, information about family, samples etc.


### Depreication Warnings:
`bam_file`, `bam_path` and `alignment_path` are redundant in internal usage. Future versions of Scout will only
support `alignment_path`.



### The Configuration File
The basic structure of a load config looks like:


```yaml
analysis_date: datetime(optional)
cnv_report: str(optional)
coverage_qc_report: str(optional)
cohorts: list(optional)
collaborators: list(optional)
coverage_qc_report: ?
default_gene_panels: list[str](optional)
delivery_report:
family: str(mandatory)
gene_fusion_report: str(optional)
gene_fusion_report_research: str(optional)gene_panels: list[str](optional)
human_genome_build: str(optional)
lims_id: str(optional)
madeline: str(optional)
multiqc: str(optional)
owner: str(mandatory)
peddy_check: str(optional)
peddy_ped: str(optional)
peddy_sex: str(optional)
phenotype_terms: list(optional)
rank_model_version: str(optional)
rank_score_threshold: float(optional)
samples:
  - alignment_path: str(optional) # path to bam file
    analysis_type: str(optional), [external, mixed, panel, unknown, wes, wgs]
    bam_file: str(optional) # WARNING: WILL BE DEPRECATED
    bam_path: str(optional) # WARNING: WILL BE DEPRECATED
    capture_kit: str(optional)
    chromograph_images (optional):
        autozygous: str(optional)
        coverage: str(optional)
        upd_regions: str(optional)
        upd_sites: str(optional)
    confirmed_parent:
    father: str(if set, sample_id must exist in samples)
    is_sma: bool(optional)
    is_sma_carrier: bool(optional)
    mother: str(if set, id must exist in samples)
    msi: str(optional) # Microsatellite instability [0,60]
    phenotype: str(mandatory), [affected, unaffected, unknown] 
    rhocall_bed: str(optional) # path to bed file
    rhocall_wig: str(optional) # path to wig file
    sample_id: str(mandatory)
    sample_name: str(optional)
    sex: str(mandatory), [male, female, unknown]
    smn1_cn:
    smn2_cn:
    smn2delta78_cn:
    smn_27134_cn:
    tiddit_coverage_wig: str(optional) # path to wig file
    tissue_type: str(optional)
    tmb: str(optional) # Tumor mutational burder [0,1000]
    tumor_purity: float # [0.1,1]
    tumor_type: str(optional)
    upd_regions_bed: str(optional) # path to bed file
    upd_sites_bed: str(optional) # path to bed file
    vcf2cytosure: str(optional) # path to CGH file
smn_tsv: str(optional)
synopsis: str(optional)
sv_rank_model_version: str(optional)
track: list[str][optional]
vcf_file:
    vcf_cancer: str(optional)
    vcf_cancer_research: str(optional)
    vcf_cancer_sv: str(optional)
    vcf_cancer_sv_research: str(optional)
    vcf_snv: str(optional)
    vcf_snv_research: str(optional)
    vcf_str: str(optional)
    vcf_sv: str(optional)
    vcf_sv_research: str(optional)

```




Let's go through each field:


- **analysis_date** time for analysis in datetime format. Defaults to time of uploading
- **cnv_report** path to the CNV report file
- **coverage_qc_report** path to static coverage and qc report file
- **default_gene_panels** list of default gene panels. Variants from the genes in the gene panels specified will be shown when opening the case in scout
- **family** each case has to have a family id
- **gene_fusion_report** path to a static file containing a gene fusion report produced by [Arriba][arriba]. Generated from default clinical data.
- **gene_fusion_report_research** path to a static file containing a gene fusion report produced by [Arriba][arriba]. Generated from research data.
- **gene_panels** list of gene panels. This will specify what panels the case has been run with
- **human_genome_build** what genome version was used.
- **madeline** path to a madeline pedigree file in xml format
- **multiqc** path to a [multiqc][multiqc] report with arbitrary information
- **owner** each case has to have a owner, this refers to an existing institute in the scout instance
- **peddy_check** path to a [peddy][peddy] ped check file
- **peddy_ped** path to a [peddy][peddy] ped file with an analysis of the pedigree based on variant information
- **peddy_sex** path to a [peddy][peddy] ped sex check file
- **rank model version** which rank model that was used when scoring the variants
- **rank_score_treshold** only include variants with a rank score above this treshold
- **samples** list of samples included in the case
	- *alignment_path* Path to bam file to view alignments
	- *analysis_type* specifies the analysis type for the sample
	- *bam_file* Path to bam file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*
	- *bam_path* Path to bam file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*
	- *capture_kit* for exome specifies the capture kit
	- *expected_coverage* the level of expected coverage
	- *father* sample id for father or 0
	- *mother* sample id for mother or 0
	- *phenotype* specifies the affection status of the sample in human readable format
	- *rhocall_bed* Path to bed file to view alignments (Reference)[https://github.com/dnil/rhocall]
	- *rhocall_wig* Path to wig file to view alignments (Reference)[https://github.com/dnil/rhocall]
	- *samlple_id* identifyer for a sample
        - *sample_name*: optional str
        - *smn1_cn*
        - *smn2_cn*
        - *smn2delta78_cn*
	- *sex* specifies the sex of the sample in human readable format
	- *tiddit_coverage_wig* Path to wig file to view alignments (Reference)[https://github.com/SciLifeLab/TIDDIT]
	- *upd_regions_bed* Path to bed file to view alignments (Reference)[https://github.com/bjhall/upd]
	- *upd_sites_bed* Path to bed file to view alignments (Reference)[https://github.com/bjhall/upd]
        - *msi* Microsatellite instability
        - *tiddit_coverage_wig*
        - *tissue_type* What tissue the sample originates from
        - *tmb* Tumor mutational burden
        - *tumor_purity* Purity of tumor sample
        - *tumor_type* Type of tumor
        - *vcf2cytosure* Path to CGH file to allow download per individual
- **SV rank model version** the SV rank model version used when scoring SV variants
- **vcf_cancer**
- **vcf_cancer_research**
- **vcf_snv** path to snv vcf file
- **vcf_snv_research** path to vcf file with all variants
- **vcf_sv**
- **vcf_sv_research**



### Minimal config

Here is an example of a minimal load config:

```yaml
---

owner: cust004

family: '1'
samples:
  - analysis_type: wes
    sample_id: NA12878
    capture_kit: Agilent_SureSelectCRE.V1
    father: 0
    mother: 0
    sample_name: NA12878
    phenotype: affected
    sex: male
    expected_coverage: 30

vcf_snv: scout/demo/643594.clinical.vcf.gz
```

### CGH (vcf2cytosure) for download
By giving a path to each individual vcf2cytosure-file these are made available
for download on the case page. Such SV files can be visualized using standard arrayCGH
analysis tools. See [vcf2cytosure](https://github.com/NBISweden/vcf2cytosure/blob/master/README.md).

[peddy]: https://github.com/brentp/peddy
[multiqc]: https://github.com/ewels/multiqc
[arriba]: https://arriba.readthedocs.io/en/latest/
