# The load config

Scout have the possibility to store loads of information about a case and the samples that are included. It is cumbersome to specify to many parameters on the command line so there is an option to give this information in a yaml formated config file.
Here we can give scout some meta information about the analysis, how it was performed, information about family, samples etc.

The basic structure of a load config looks like:


```yaml
owner: str(mandatory)

family: str(mandatory)
samples:
  - analysis_type: str(optional), [wgs,wes,panel,external]
    sample_id: str(mandatory)
    capture_kit: str(optional)
    father: str(mandatory)
    mother: str(mandatory)
    sample_name: str(mandatory)
    phenotype: str(mandatory), [affected, unaffected, unknown]
    sex: str(mandatory), [male, female, unknown]
    expected_coverage: int(mandatory)
    vcf2cytosure: str(optional) # path to CGH file
    bam_path: str(optional) # path to bam file
    rhocall_bed: str(optional) # path to bed file
    rhocall_wig: str(optional) # path to wig file
    upd_regions_bed: str(optional) # path to bed file
    upd_sites_bed: str(optional) # path to bed file
    tiddit_coverage_wig: str(optional) # path to wig file

    tissue_type: str(optional)
    tumor_type: str(optional)
    tmb: str(optional) # Tumor mutational burder [0,1000]
    msi: str(optional) # Microsatellite instability [0,60]
    tumor_purity: float # [0.1,1]

vcf_snv: str(optional)
vcf_sv: str(optional)
vcf_cancer: str(optional)
vcf_snv_research: str(optional)
vcf_sv_research: str(optional)
vcf_cancer_research: str(optional)

madeline: str(optional)

peddy_ped: str(optional)
peddy_check: str(optional)
peddy_sex: str(optional)

multiqc: str(optional)
cnv_report: str(optional)

default_gene_panels: list[str](optional)
gene_panels: list[str](optional)

# ATM rare or cancer
track: list[str][optional]

# meta data
rank_model_version: str(optional)
sv_rank_model_version: str(optional)
rank_score_threshold: float(optional)
analysis_date: datetime(optional)
human_genome_build: str(optional)
```

Let's go through each field:

- **owner** each case has to have a owner, this refers to an existing institute in the scout instance
- **family** each case has to have a family id
- **samples** list of samples included in the case
	- *analysis_type* specifies the analysis type for the sample
	- *samlple_id* identifyer for a sample
	- *capture_kit* for exome specifies the capture kit
	- *father* sample id for father or 0
	- *mother* sample id for mother or 0
	- *phenotype* specifies the affection status of the sample in human readable format
	- *sex* specifies the sex of the sample in human readable format
	- *expected_coverage* the level of expected coverage
	- *bam_file* Path to bam file to view alignments
	- *rhocall_bed* Path to bed file to view alignments (Reference)[https://github.com/dnil/rhocall]
	- *rhocall_wig* Path to wig file to view alignments (Reference)[https://github.com/dnil/rhocall]
	- *upd_regions_bed* Path to bed file to view alignments (Reference)[https://github.com/bjhall/upd]
	- *upd_sites_bed* Path to bed file to view alignments (Reference)[https://github.com/bjhall/upd]
	- *tiddit_coverage_wig* Path to wig file to view alignments (Reference)[https://github.com/SciLifeLab/TIDDIT]
    - *vcf2cytosure* Path to CGH file to allow download per individual
    - *tumor_type* Type of tumor
    - *tissue_type* What tissue the sample originates from
    - *tmb* Tumor mutational burden
    - *msi* Microsatellite instability
    - *tumor_purity* Purity of tumor sample

- **vcf_snv** path to snv vcf file
- **vcf_sv**
- **vcf_snv_research** path to vcf file with all variants
- **vcf_sv_research**
- **vcf_cancer**
- **vcf_cancer_research**
- **madeline** path to a madeline pedigree file in xml format
- **peddy_ped** path to a [peddy][peddy] ped file with an analysis of the pedigree based on variant information
- **peddy_check** path to a [peddy][peddy] ped check file
- **peddy_sex** path to a [peddy][peddy] ped sex check file
- **multiqc** path to a [multiqc][multiqc] report with arbitrary information
- **cnv_report** path to the CNV report file
- **default_gene_panels** list of default gene panels. Variants from the genes in the gene panels specified will be shown when opening the case in scout
- **gene_panels** list of gene panels. This will specify what panels the case has been run with
- **rank model version** which rank model that was used when scoring the variants
- **SV rank model version** the SV rank model version used when scoring SV variants
- **rank_score_treshold** only include variants with a rank score above this treshold
- **analysis_date** time for analysis in datetime format. Defaults to time of uploading
- **human_genome_build** what genome version was used.

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
