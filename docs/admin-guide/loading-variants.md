# Variant loading

This document will describe the process of variant loading, how it is done and why.

## Loading

Variants are loaded as part of the case load process. The location of variant call format files (VCF) is given in
the case load config, and are parsed using CyVCF. Variants can be annotated to display a lot more useful information
beyond genomics nucleotide change. See [Annotations](./annotations.md).

## Rank Score

In Scout rank score is a central theme. Rank Scores is a estimation on how potentially dangerous a variant is, similar to the CADD score with the intention of work with all types of variation.
The uploading of variants is based on a rank score threshold, this is to avoid to clog the database with millions of variants that we at the moment have a hard time to say anything about.

The rank score is a summary of the annotations of a variant. Rank scores are calculated and annotated by [GENMOD][genmod]

## Clinical and Research variants

The system is designed to accept `clinical` and `research` level variants in separate files. Clinical variants are accompanied with
clinical gene panels defined on the case. This separation further lowers the risk of incidental findings, and clarifies when genetic research
is performed in contrast to clinical testing or screening.

## Variant category

A variant belongs to a category, and is displayed in distinct variantS and variant views accordingly. Categories include "snv", "sv", "mei", "str", "cancer" and "cancer_sv".
Variants of different category are loaded from different VCF files.

## OMICS variants

Scout can load OMICS variants, similar to variants but from other sources than genomic DNA sequencing, e.g. DROP WTS expression outliers.
These are displayed in a different view, similar to the DNA variants.

## Loading variants for a preexisting case without a load config

Note that the files have to be linked with the case - if they are not use `scout update case`.

```bash
scout update case -n case_name -i institue --vcf-str /my_pipeline/my_case/my_case.str.vcf.gz
scout load variants --str-clinical
```

## Loading OMICS variants for a preexisting case without a load config

Note that the files have to be linked with the case - if they are not use `scout update case`.
If the sample IDs in your OMICS files do not correspond to your DNA sample IDs, and they are not provided in the
case config, use `scout update individual` to set the `omics_sample_id` for each of the individuals.

```bash
scout update individual -c case_id -n individual_display_name omics_sample_id my_rna_sample_id
scout update case -n case_name -i institue --fraser /my_pipeline/my_case/my_rna_sample.drop.fraser.tsv --outrider /my_pipeline/my_case/my_rna_sample.drop.outrider.tsv
scout load variants --outlier
```


[genmod]: https://github.com/moonso/genmod

