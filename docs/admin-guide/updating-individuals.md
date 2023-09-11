# Updating case individuals tracks using the command line.

After a case is loaded and saved in the database, some individual-specific keys can be modified without having to re-upload the entire case.
These key/values are relative to the optional tracks available for the individual and must be set at the individual level (each of them specified for each individual).

The command line command used to update individuals track is the following:
```
Usage: scout update individual [OPTIONS] [KEY] [VALUE]

  Update information on individual level in Scout

Options:
  -c, --case-id TEXT  Case id  [required]
  -n, --ind TEXT      Individual display name
```
And the tracks that can be updated are the following:
- bam_file
- rna_alignment_path
- mt_bam
- vcf2cytosure
- rhocall_bed
- rhocall_wig
- tiddit_coverage_wig
- upd_regions_bed
- upd_sites_bed
- splice_junctions_bed
- rna_coverage_bigwig


## Description of custom individual tracks:

### DNA-sequencing alignment files
The following files are used by the [igv.js](https://github.com/igvteam/igv.js/wiki/Alignment-Track) integrated browser to display sequence variation alignments. The igv.js browser can be opened by clicking on the relative link (button) present on variants page. The link is displayed only if at least one individual of the case contains one bam_file or mt_bam track saved.

| key name            | key value     |
| --------------------|:-------------:|
| bam_file            | path to a bam/cram alignment file                           |
| mt_bam              | path to a downsampled mitochondrial bam/cram alignment file |
| rhocall_bed         | path to rhocall output bed file                             |
| rhocall_wig         | path to rhocall output wig file                             |
| tiddit_coverage_wig | path to tiddit wig coverage file                            |
| upd_regions_bed     | path to upd_regions_bed                                     |
| upd_sites_bed       | path to vcf2cytosure file                                   |

rhocall_bed and rhocall_wig files are both obtained from [rhocall](https://github.com/dnil/rhocall), a software that calls and annotates autozygosity from VCF files.

tiddit_coverage_wig files are obtained from [tiddit](https://github.com/SciLifeLab/TIDDIT), a software in turn is used to call structural variants.

upd_regions_bed and upd_sites_bed files are created from VCF files using the [upd tool](https://github.com/bjhall/upd).


### RNA-sequencing splice junctions files
These files are both required by the integrated [splice junction track](https://github.com/igvteam/igv.js/wiki/Splice-Junctions) view of igv.js.

| key name             | key value     |
| -------------------- |:-------------:|
| splice_junctions_bed | path to An indexed junctions .bed.gz file obtained             |
| rna_coverage_bigwig  | path to coverage islands file generated from bam or cram files |

splice_junctions_bed is obtained from from STAR v2 aligner *.SJ.out.tab file and rna_coverage_bigwig contains coverage islands obtained from RNA-seq bam or cram alignments

A link to the splice junction view is present on variants pages of cases with at least one individual with these files.

### vcf2cytosure file

| key name      | key value     |
| ------------- |:-------------:|
| vcf2cytosure | path to vcf2cytosure file  |

[vcf2cytosure](https://github.com/NBISweden/vcf2cytosure) is a tool that converts a VCF with structural variations to the “.CGH” format used by the commercial [CytoSure Interpret Software](https://www.ogt.com/products/product-search/cytosure-interpret-software/) by OGT (Oxford Gene Technology). Once the individual is updated with this track, vcf2cytosure files will be available for download from the individuals table present on Scout's case page.
