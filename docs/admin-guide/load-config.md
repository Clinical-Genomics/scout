# The Load Config File


Scout have the possibility to store loads of information about a case and the samples that are included. It is cumbersome to specify to many parameters on the command line so there is an option to give this information in a yaml formated config file.
Here we can give scout some meta information about the analysis, how it was performed, information about family, samples etc.


### Depreication Warnings:
`bam_file`, `bam_path` and `alignment_path` are redundant in internal usage. Future versions of Scout will only
support `alignment_path`.


### Configuration Parameters
Below are available configuration parameters for a Scout case. Names marked with asterix (*) are mandatory. 

- **analysis_date(*)** Time for analysis in datetime format. Defaults to time of uploading. Example `2016-10-12 14:00:46`
- **cnv_report** Path to the CNV report file.
- **coverage_qc_report** Path to static coverage and qc report file.
- **cohorts** List of strings, for meta organising study participants or cases.
- **collaborators** list of collaborators
- **coverage_qc_report** Path to html file with coverage and qc report.
- **default_gene_panels** List of default gene panels. Variants from the genes in the gene panels specified will be shown when opening the case in scout
- **delivery_report**: Path to html delivery report.
- **family(*)**  Unique id of family in the configuration.
- **gene_fusion_report** Path to a static file containing a gene fusion report produced by [Arriba][arriba]. Generated from default clinical data.
- **gene_fusion_report_research** Path to a static file containing a gene fusion report produced by [Arriba][arriba]. Generated from research data.
- **gene_panels** List of gene panels. This will specify what panels the case has been run with.
- **human_genome_build** Version of genome version used.
- **lims_id** Lims Id used.
- **madeline** Path to a madeline pedigree file in xml format.
- **multiqc** Path to a [multiqc][multiqc] report with arbitrary information.
- **owner(*)**  Institute who owns current case. Must refer to existing institute
- **peddy_check** Path to a [peddy][peddy] ped check file.
- **peddy_ped** Path to a [peddy][peddy] ped file with an analysis of the pedigree based on variant information.
- **peddy_sex** Path to a [peddy][peddy] ped sex check file.
- **phenotype_terms** List of phenotype terms.
- **rank model version** Which rank model that was used when scoring the variants.
- **rank_score_treshold** Only include variants with a rank score above this treshold.
- **samples** List of samples included in the case:
	- **alignment_path** Path to bam file to view alignments
	- **analysis_type** specifies the analysis type for the sample
	- **bam_file** Path to bam file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*
	- **bam_path** Path to bam file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*
	- **capture_kit** for exome specifies the capture kit
        - **chromograph_images**:
            - **autozygous**: Path to file.
            - **upd_regions**: Path to file.
            - **upd_sites**: Path to file.
        - **confirmed_parent**: True if parent confirmed.
	- **expected_coverage** The level of expected coverage.
	- **father** Sample id for father or 0
        - **is_sma**: True / False if SMA status determined - None if not done.
        - **is_sma_carrier**:  # True / False if SMA carriership determined - None if not done.
	- **mother** sample id for mother or 0
        - **msi** Microsatellite instability [0-60]
	- **phenotype(*)** Specifies the affection status {affected, unaffected, unknown}  
	- **rhocall_bed** Path to bed file to view alignments [Reference][rhocall]
	- **rhocall_wig** Path to wig file to view alignments [Reference][rhocall]
	- **samlple_id(*)** Identifyer for a sample 
        - **sample_name**: Name of sample.
        - **sex (*)**:{male, female, unknown} 
        - **smn1_cn** int Copynumber
        - **smn2_cn** int Copynumber
        - **smn2delta78_cn** int Copynumber
	- **sex(*)** Sex of the sample in human readable format
	- **tiddit_coverage_wig** Path to wig file to view alignments [Reference][tiddit]
        - **tissue_type** Sample tissue origin i.e. blood, muscle, 
        - **tmb** Tumor mutational burden
        - **tumor_purity** Purity of tumor sample
        - **tumor_type** Type of tumor
	- **upd_regions_bed** Path to bed file to view alignments [Reference][bjhall]
	- **upd_sites_bed** Path to bed file to view alignments [Reference][bjhall]
        - **vcf2cytosure** Path to CGH file to allow download per individual
- **smn_tsv** Path to an SMN TSV file
- **synopsis** Synopsis of case.
- **sv_rank_model_version** String
- **track** Type of track: {"rare", "cancer"}. Default: "rare".
- **vcf_file** A dictionary with vcf files
- **sv_rank_model_version** the SV rank model version used when scoring SV variants
- **vcf_cancer** Path to canver vcf file.
- **vcf_cancer_research** Path to vcf file with all variants.
- **vcf_snv** Path to snv vcf file.
- **vcf_snv_research** Path to vcf file with all variants.
- **vcf_sv** Path to sv vcf file
- **vcf_sv_research** Path to vcf file with all variants.



### Example Minimal config

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

[arriba]: https://arriba.readthedocs.io/en/latest/
[bjhall]: https://github.com/bjhall/upd
[multiqc]: https://github.com/ewels/multiqc
[peddy]: https://github.com/brentp/peddy
[tiddit]: https://github.com/SciLifeLab/TIDDIT
[rhocall]: https://github.com/dnil/rhocall