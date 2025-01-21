# Loading Scout cases

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

# metadata
rank_model_version: '1.12'
sv_rank_model_version: '1.5'
rank_score_threshold: -100
analysis_date: 2016-10-12 14:00:46
human_genome_build: '37'

```

#### Adding custom reports to the case
A number of case-associated reports (supported formats: HTML, PDF, Excel) can be loaded and displayed/downloaded on the case sidebar page:

<img width="227" alt="image" src="https://user-images.githubusercontent.com/28093618/201290117-33b1ea53-eb8e-4e80-a5df-edba8b6595fe.png">

While case General report and mtDNA report (the latter only available for non-cancer cases) are generated the moment a user clicks on their link, other types of reports are pre-existing documents that can be associated with the case immediately when it is loaded in Scout (by adding them to the case load config file) or later, using the command line.

Available types or case reports:
- **cnv**: Copy Number Variants Report (PDF), available only for cancer cases
- **cov_qc**: Coverage QC Report (HTML), available only for cancer cases
- **delivery**: Delivery Report (HTML)
- **exe_ver**: Pipeline detailed software versions (YAML)
- **gene_fusion**: A report (PDF) showing gene fusions from RNA-Seq data, analysis limited to the clinical gene list
- **gene_fusion_research**: A report (PDF) showing gene fusions from RNA-Seq data, performed on all genes
- **multiqc**: [MultiQC](https://multiqc.info/) Report (HTML)
- **multiqc_rna**: MultiQC RNA report (HTML)
- **reference_info**: Pipeline detailed reference file versions (YAML)
- **RNAfusion_inspector**: [nf-core rnafusion][nfcore-rnafusion] RNA Fusion Inspector file (HTML)
- **RNAfusion_inspector_research**: [nf-core rnafusion][nfcore-rnafusion] research RNA Fusion Inspector file (HTML)
- **RNAfusion_report**: [nf-core rnafusion][nfcore-rnafusion] RNA fusion report file (HTML)
- **RNAfusion_report_research**: [nf-core rnafusion][nfcore-rnafusion] research RNA fusion report file (HTML)


All these reports reflect the items present in [this dictionary](https://github.com/Clinical-Genomics/scout/blob/b0cfc8795392ed7e1b223eeaa5ad5590fc6e8892/scout/constants/case_tags.py#L4)


Use the following command to load/update a report for a pre-existing case:

```
scout load report -t <report-type>

Usage: scout load report [OPTIONS] CASE_ID REPORT_PATH

  Load a report document for a case.

Options:
  -t, --report-type [delivery|cnv|cov_qc|exe_ver|multiqc|multiqc_rna|gene_fusion|gene_fusion_research|reference_info|RNAfusion_inspector|RNAfusion_inspector_research|RNAfusion_report|RNAfusion_report_research]
                                  Type of report  [required]
```

#### Adding custom images to a case

Scout can display custom images as new panels on the case view or variant view which could be used to display analysis results from a separate pipeline. The custom images are defined in the case config file and stored in the database. Scout currently supports     `gif`, `jpeg`, `png` and `svg` images.

The syntax for loading an image differed depending on where they are going to be displayed. Images on the caes view can be grouped into different groups that are displayed as accordion-type UI elemment named after the group. Images can be associated with stru    ctural variants with a given hgnc symbol.

The fields `title`, `description` and `path` are mandatory regarless of location. The image size can be defined with the optional parameters `width` and `height`. If you dont specify a unit its going to default to use pixels as unit. *Note*: adding images lar    ger than 16mb are not reccomended as it might degrade the performance.

``` yaml

custom_images:
  case_images:
    group_one:
      - title: <string> title of image [mandatory]
        description: <string> replacement description of image [mandatory]
        width: <string> 500px
        height: <string> 100px
        path: <string> scout/demo/images/custom_images/640x480_one.png [mandatory]
      - title: <string> A jpg image [mandatory]
        description: <string> A very good description [mandatory]
        width: <string> 500px
        path: <string> scout/demo/images/custom_images/640x480_two.jpg [mandatory]
    group_two:
      - title: <string> An SVG image [mandatory]
        description: <string> Another very good description
        path: <string> scout/demo/images/custom_images/640x480_three.svg [mandatory]
  str_variants_images:
    - title: <string> title of image [mandatory]
      str_repid: AFF2 [mandatory]
      description: <string> replacement description of image [mandatory]
      width: <string> 500px
      height: <string> 100px
      path: <string> scout/demo/images/custom_images/640x480_one.png [mandatory]
    - title: <string> A jpg image [mandatory]
      str_repid: AFF2 [mandatory]
      description: <string> A very good description [mandatory]
      width: <string> 500px
      path: <string> scout/demo/images/custom_images/640x480_two.jpg [mandatory]

```

##### Loading multiple images with wildcards

If you have multiple images you would like to associate with a different variants you can use wildcards to reduce the number of lines in the load config file. For example, you have two images `640x480_AR.svg` and `640x480_ATN1.svg` that should be attaced to variants in replicions AR and ATN1. Instead of writing a long list with one entry per image you could use wildcards to flag which parts of the path name that corresponds to the repid. Wildcards are a variable name surrounded by curly brackets, `{VARIALBE_NAME}`. The varible name can contain letters, numbers and underscore and score.

When the images are loaded into the database the algorithm finds files matching the pattern and substitutes the wildcard with the sting. In other words will this enable the user to extract information encoded in the path and populate the configuration with it.

Given the two files above will this configuration

``` yaml
custom_images:
  str_variants_images:
    - title: <string> A jpg image {REPID} [mandatory]
      str_repid: {REPID} [mandatory]
      path: <string> scout/demo/images/custom_images/640x480_{REPID}.jpg [mandatory]
```

be equivalent to

``` yaml
custom_images:
  str_variants_images:
    - title: <string> An image of AR
      str_repid: AR
      path: <string> scout/demo/images/custom_images/640x480_AR.jpg
    - title: <string> An image of ATN1
      str_repid: ATN1
      path: <string> scout/demo/images/custom_images/640x480_ATN1.jpg
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

[nfcore-rnafusion]: https://nf-co.re/rnafusion
