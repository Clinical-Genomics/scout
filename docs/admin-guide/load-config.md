# The Load Config File

A case and its individuals (or samples, in cancer track) can be uploaded into Scout using specially formatted .yaml config files. Config files contain information about the analysis, panels used, path to VCF and eventual alignment files and more. The following template illustrates the basic structure of the .yaml config file:

The format is [Yaml][yaml].

Example configuration files are found here: `<scout root dir>/scout/demo/643594.config.yaml` or on [Github](https://github.com/Clinical-Genomics/scout/blob/update_config_docs-210428/scout/demo/643594.config.yaml).

### Deprecation Warnings:
`bam_file`, `bam_path` and `alignment_path` are redundant in internal usage. Future versions of Scout will only
support `alignment_path`.


### Configuration Parameters
Below are available configuration parameters for a Scout case. Names marked with asterix (*) are mandatory.

- **analysis_date(*)** _Datetime_ Time for analysis in datetime format. Defaults to time of uploading. Example `2016-10-12 14:00:46`.
- **cnv_report** _String_ Path to the CNV report file.
- **coverage_qc_report** _String_ Path to static coverage and QC report file.
- **cohorts** _List of strings_ Meta organising study participants or cases.
- **collaborators** _List of strings_ List of collaborators.
- **coverage_qc_report** _String_ Path to HTML file with coverage and QC report.
- **default_gene_panels** _List of strings_ List of default gene panels. Variants from the genes in the gene panels specified will be shown when opening the case in scout.
- **delivery_report** _String_: Path to HTML delivery report.
- **exe_ver**: Pipeline detailed software versions (YAML)
- **family(*)**  _String_ Unique ID of the case.
- **family_name**  _String_ Optional name of the case.
- **gene_fusion_report** _String_ Path to a static gene fusion report produced by [Arriba][arriba] containing only clinical fusions (a subset of all detected fusions).
- **gene_fusion_report_research** _String_ Path to a static gene fusion report produced by [Arriba][arriba] containing all detected fusions.
- **gene_panels** _List of strings_ List of gene panels. Specifies what panels the case has been run with.
- **human_genome_build** _String_ Version of genome version used, 37 or 38. Defaults to 37.
- **lims_id** _String_ Case ID in Lims
- **madeline** _String_ Path to a madeline pedigree file in XML format.
- **multiqc** _String_ Path to a [multiqc][multiqc] report with arbitrary information.
- **multiqc_rna** _String_ Path to a [nf-core/rnafusion multiqc][rna-multiqc] report with arbitrary information.
- **omics_files** _List_ List of multiomics results files for the case:
    - **fraser** _String_ Path to TSV file to parse WTS [DROP][drop] FRASER splice outlier omics variants as produded by e.g. [Tomte][tomte]
    - **outrider** _String_ Path to TSV file to parse WTS [DROP][drop] OUTRIDER expression outlier omics variants as produded by e.g. [Tomte][tomte]
- **owner(*)**  _String_ Institute who owns current case. Must refer to existing institute.
- **peddy_check** _String_ Path to a [peddy][peddy] ped check file.
- **peddy_ped** _String_ Path to a [peddy][peddy] ped file with an analysis of the pedigree based on variant information.
- **peddy_sex** _String_ Path to a [peddy][peddy] ped sex check file.
- **phenotype_terms** _List of strings_ List of phenotype terms.
- **rank model version** _String_ Which rank model that was used when scoring the variants.
- **rank_score_threshold** _Float_ Only include variants with a rank score above this threshold.
- **reference_info**: Pipeline detailed reference file versions (YAML)
- **RNAfusion_inspector** _String_ Path to HTML [nf-core/rnafusion inspector][rnafusion-inspector] report containing only clinical fusions (a subset of all detected fusions).
- **RNAfusion_inspector_research** _String_ Path to HTML [nf-core/rnafusion inspector][rnafusion-inspector] report containing all detected fusions.
- **RNAfusion_report** _String_ Path to HTML [nf-core/rnafusion report][rnafusion-report] containing only clinical fusions (a subset of all detected fusions).
- **RNAfusion_report_research** _String_ Path to HTML [nf-core/rnafusion report][rnafusion-report] containing all detected fusions.
- **rna_human_genome_build** _String_ Version of reference genome used for RNA components of build. "37" or "38", default "38".
- **rna_delivery_report** _String_: Path to HTML RNA delivery report.
- **samples** _List_ List of samples included in the case:
    - **alignment_path** _String_ Path to BAM/CRAM file to view alignments.
    - **analysis_type** _String_ Specifies the analysis type for the sample. Options: {wgs, wes, panel, unknown, external}.
    - **assembly_alignment_path** _String_ Path to BAM/CRAM file to view de novo assembly alignments.
    - **bam_file** _String_ Path to BAM/CRAM file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*.
    - **bam_path** _String_ Path to BAM/CRAM file to view alignments **WARNING:** Soon to be deprecated, use *alignment_path*.
    - **capture_kit** _String_ Exome specifies the capture kit.
    - **chromograph_images** _List_
        - **autozygous** _String_ Path to file.
        - **coverage** _String_ Path to file.
        - **upd_regions** _String_ Path to file.
        - **upd_sites** _String_ Path to file.
    - **confirmed_parent** _Bool_ True if parent confirmed.
    - **d4_path** _String_ Path to [.d4 file][d4_file]. Required for Chanjo2 integration
    - **expected_coverage** _Int_ The level of expected coverage.
    - **father** _String/Int_ Sample ID for father or 0.
    - **hrd** _Int_ Homologous recombination deficiency.
    - **is_sma** _Bool/None_ if SMA status determined - None if not done.
    - **is_sma_carrier**  _Bool/None_  # True / False if SMA carriership determined - None if not done.
    - **minor_allele_frequency_wig** _String_ Path to minor allele frequency bigwig [Reference][hificnv].
    - **mitodel** _String_ Path to mitodel file.
    - **mother** _String/Int_ Sample ID for mother or 0.
    - **msi** _Int_ Microsatellite instability [0-60].
    - **mt_bam** _String_ Path to the reduced mitochondrial BAM/CRAM alignment file.
    - **paraphase_alignment_path** _String_ Path to BAM/CRAM file to view Paraphase alignments [Reference][paraphase].
    - **phenotype(*)** _String_ Specifies the affection status {affected, unaffected, unknown}.
    - **reviewer** _List_ [Reference][srs]
      - **alignment** _String_ Path to BAM/CRAM file to view STR alignments
      - **alignment_index** _String_ Path to BAM/CRAM index file to view STR alignments
      - **vcf** _String_ Path to STR VCF file to view STR alignments
      - **catalog** _String_ Path or URL to REViewer catalog JSON file to view STR alignments
      - **reference** _String_ Path or URL for REViewer to reference sequence for the individual STR alignment
    - **rna_alignment_path** _String_ Path to RNA alignment file (BAM/CRAM)
    - **rna_coverage_bigwig** _String_ Path to coverage islands file generated
    - **omics_sample_id** _String_ Sample ID for RNA, as in outliers files
    - **rhocall_bed** _String_ Path to BED file to view alignments [Reference][rhocall].
    - **rhocall_wig** _String_ Path to WIG file to view alignments [Reference][rhocall].
    - **samlple_id(*)** _String_ Identifyer for a sample.
    - **sample_name**: _String_ Name of sample.
    - **sex (*)** _String_ One of: {male, female, unknown}. Sex of the sample in human readable format.
    - **smn1_cn** _Int_ Copynumber.
    - **smn2_cn** _Int_ Copynumber.
    - **smn2delta78_cn** _Int_ Copynumber.
    - **splice_junctions_bed** _String_ Path to indexed junctions .bed.gz file
    - **subject_id** _String_ Individual identifier - multiple samples could belong to the same individual
    - **tiddit_coverage_wig** or **coverage_wig** _String_ Path to WIG file to view alignment coverage overview from e.g. [Reference][tiddit] or [Reference][hificnv].
    - **tissue_type** _String_ Sample tissue origin i.e. blood, muscle.
    - **tmb** _Int_ Tumor mutational burden [0, 1000] (tumor case only).
    - **tumor_purity** _Float_ Purity of tumor sample [0.1, 1.0] (tumor case only).
    - **tumor_type** _String_ Type of tumor (tumor case only).
    - **upd_regions_bed** _String_ Path to BED file to view alignments [Reference][upd].
    - **upd_sites_bed** _String_ Path to BED file to view alignments [Reference][upd].
    - **vcf2cytosure** _String_ Path to CGH file to allow download per individual. Such SV files can be visualized using standard arrayCGH analysis tools. See [vcf2cytosure](https://github.com/NBISweden/vcf2cytosure/blob/master/README.md).
- **smn_tsv** _String_ Path to an SMN TSV file.
- **somalier_ancestry** _String_ Path to a [Somalier][somalier] ancestry tsv file.
- **somalier_pairs** _String_ Path to a [Somalier][somalier] pairs tsv file.
- **somalier_samples** _String_ Path to a [Somalier][somalier] samples tsv file.
- **status** _String_ Any of the following strings: 'prioritized', 'inactive', 'ignored', 'active', 'solved' or 'archived'.
- **synopsis** _String_ Synopsis of case.
- **sv_rank_model_version** _String_ Rank model that was used when scoring the variants.
- **track** _String_ Type of track: {"rare", "cancer"}. Default: "rare".
- **sv_rank_model_version** _String_ SV rank model version used when scoring SV variants.
- **vcf_cancer** _String_ Path to canver VCF file (tumor case only).
- **vcf_cancer_research** _String_ Path to VCF file with all variants (tumor case only).
- **vcf_snv** _String_ Path to SNV VCF file  containing only clinical variants (a subset of all variants).
- **vcf_snv_research** _String_ Path to VCF file with all variants.
- **vcf_sv** _String_ Path to SV VCF file containing only clinical variants (a subset of all variants).
- **vcf_sv_research** _String_ Path to VCF file with all SV variants.



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


[arriba]: https://arriba.readthedocs.io/en/latest/
[d4_file]: https://github.com/38/d4-format
[drop]: https://github.com/gagneurlab/drop
[hificnv]: https://github.com/PacificBiosciences/HiFiCNV
[multiqc]: https://github.com/ewels/multiqc
[paraphase]: https://github.com/PacificBiosciences/paraphase
[peddy]: https://github.com/brentp/peddy
[rna-multiqc]: https://nf-co.re/rnafusion/output#multiqc
[rnafusion-inspector]: https://nf-co.re/rnafusion/output#fusioninspector
[rnafusion-report]: https://nf-co.re/rnafusion/output#fusion-report
[rhocall]: https://github.com/dnil/rhocall
[somalier]: https://github.com/brentp/somalier
[srs]: https://github.com/Clinical-Genomics/Scout-REViewer-service
[tiddit]: https://github.com/SciLifeLab/TIDDIT
[tomte]: https://github.com/genomic-medicine-sweden/tomte
[upd]: https://github.com/bjhall/upd
[yaml]: https://yaml.org


