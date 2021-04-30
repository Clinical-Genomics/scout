# The Load Config File


Scout have the possibility to store loads of information about a case and the samples that are included. It is cumbersome to specify to many parameters on the command line so there is an option to give this information in a yaml formated config file.
Here we can give scout some meta information about the analysis, how it was performed, information about family, samples etc.

Format is [Yaml] [yaml].

Example configuration files are found here: `<scout root dir>/scout/demo/643594.config.yaml`

### Depreication Warnings:
`bam_file`, `bam_path` and `alignment_path` are redundant in internal usage. Future versions of Scout will only
support `alignment_path`.


### Configuration Parameters
Below are available configuration parameters for a Scout case. Names marked with asterix (*) are mandatory. 

- **analysis_date(*)** _Datetime_ Time for analysis in datetime format. Defaults to time of uploading. Example `2016-10-12 14:00:46`
- **cnv_report** _String_ Path to the CNV report file.
- **coverage_qc_report** _String_ Path to static coverage and qc report file.
- **cohorts** _List of strings_ Meta organising study participants or cases.
- **collaborators** _List of strings_ List of collaborators
- **coverage_qc_report** _String_ Path to html file with coverage and qc report.
- **default_gene_panels** _List of strings_ List of default gene panels. Variants from the genes in the gene panels specified will be shown when opening the case in scout
- **delivery_report** _String_: Path to html delivery report.
- **family(*)**  _String_ Unique id of family in the configuration.
- **gene_fusion_report** _String_ Path to a static file containing a gene fusion report produced by [Arriba][arriba]. Generated from default clinical data.
- **gene_fusion_report_research** _String_ Path to a static file containing a gene fusion report produced by [Arriba][arriba]. Generated from research data.
- **gene_panels** _List of strings_ List of gene panels. Specifies what panels the case has been run with.
- **human_genome_build** _String_ Version of genome version used.
- **lims_id** _String_ Lims Id used.
- **madeline** _String_ Path to a madeline pedigree file in xml format.
- **multiqc** _String_ Path to a [multiqc][multiqc] report with arbitrary information.
- **owner(*)**  _String_ Institute who owns current case. Must refer to existing institute
- **peddy_check** _String_ Path to a [peddy][peddy] ped check file.
- **peddy_ped** _String_ Path to a [peddy][peddy] ped file with an analysis of the pedigree based on variant information.
- **peddy_sex** _String_ Path to a [peddy][peddy] ped sex check file.
- **phenotype_terms** _List of strings_ List of phenotype terms.
- **rank model version** _String_ Which rank model that was used when scoring the variants.
- **rank_score_treshold** _Float_ Only include variants with a rank score above this treshold.
- **samples** _List_ List of samples included in the case:
	- **alignment_path** _String_ Path to bam file to view alignments
	- **analysis_type** _String_ Specifies the analysis type for the sample
	- **bam_file** _String_ Path to bam file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*
	- **bam_path** _String_ Path to bam file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*
	- **capture_kit** _String_ Exome specifies the capture kit
	- **chromograph_images** _List_
		- **autozygous** _String_ Path to file.
		- **upd_regions** _String_ Path to file.
		- **upd_sites** _String_ Path to file.
	- **confirmed_parent** _Bool_ True if parent confirmed.
	- **expected_coverage** _Int_ The level of expected coverage.
	- **father** _String/Int_ Sample id for father or 0
	- **is_sma** _Bool/None_ if SMA status determined - None if not done.
	- **is_sma_carrier**  _Bool/None_  # True / False if SMA carriership determined - None if not done.
	- **mother** _String/Int_ Sample id for mother or 0
	- **msi** _Int_ Microsatellite instability [0-60]
	- **phenotype(*)** _String_ Specifies the affection status {affected, unaffected, unknown}  
	- **rhocall_bed** _String_ Path to bed file to view alignments [Reference][rhocall]
	- **rhocall_wig** _String_ Path to wig file to view alignments [Reference][rhocall]
	- **samlple_id(*)** _String_ Identifyer for a sample 
	- **sample_name**: _String_ Name of sample.
	- **sex (*)**: _String_ One of: {male, female, unknown} 
	- **smn1_cn** _Int_ Copynumber
	- **smn2_cn** _Int_ Copynumber
	- **smn2delta78_cn** _Int_ Copynumber
	- **sex(*)** _String_ Sex of the sample in human readable format
	- **tiddit_coverage_wig** _String_ Path to wig file to view alignments [Reference][tiddit]
	- **tissue_type** _String_ Sample tissue origin i.e. blood, muscle, 
	- **tmb** _String_ Tumor mutational burden
	- **tumor_purity** _Float_ Purity of tumor sample [0.1, 1.0]
	- **tumor_type** _String_ Type of tumor
	- **upd_regions_bed** _String_ Path to bed file to view alignments [Reference][bjhall]
	- **upd_sites_bed** _String_ Path to bed file to view alignments [Reference][bjhall]
	- **vcf2cytosure** _String_ Path to CGH file to allow download per individual
- **smn_tsv** _String_ Path to an SMN TSV file
- **synopsis** _String_ Synopsis of case.
- **sv_rank_model_version** _String_ Rank model that was used when scoring the variants
- **track** _String_ Type of track: {"rare", "cancer"}. Default: "rare".
- **vcf_file** _String_ Path to dictionary with vcf files
- **sv_rank_model_version** _String_ SV rank model version used when scoring SV variants
- **vcf_cancer** _String_ Path to canver vcf file.
- **vcf_cancer_research** _String_ Path to vcf file with all variants.
- **vcf_snv** _String_ Path to snv vcf file.
- **vcf_snv_research** _String_ Path to vcf file with all variants.
- **vcf_sv** _String_ Path to sv vcf file
- **vcf_sv_research** _String_ Path to vcf file with all variants.



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
[yaml]: https://yaml.org