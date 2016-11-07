# Annotations

This page will describe what is displayed in scout, what the different annotations mean and how they are parsed from the vcf file.

## Frequencies

### 1000G ###

The frequency from the [1000G][1000g] population database. This is collected from the key **1000GAF** from the info field of the vcf record and expects a single float.

### 1000G_MAX_AF ###

The maximum allele frequency of all populations in the 1000G population database. This is collected from the key **1000G_MAX_AF** from the info field of the vcf record and expects a single float.

### ExAC ###

The frequency from the ExAC population database. This is collected from the key **EXACAF** from the info field of the vcf record and expects a single float.

### ExAC_MAX_AF ###

The maximum allele frequency of all populations ExAC population database. This is collected from the key **ExAC_MAX_AF** from the info field of the vcf record and expects a single float.

## Severity ##

### CADD score ###

The predicted deleteriousness for a variants. This is collected from the key **CADD** from the info field of the vcf record and expects a single float.

## Conservation ##

### Gerp ###

The gerp conservation string. This is collected from the key **GERP++_RS_prediction_term** from the info field of the vcf record and expects a string.

### phastCons ###

The gerp conservation string. This is collected from the key **GERP++_RS_prediction_term** from the info field of the vcf record and expects a string.

### phylop ###

The phylop 100 way predicted conservation string. This is collected from the key **phyloP100way_vertebrate_prediction_term** from the info field of the vcf record and expects a string.

[1000g]: http://www.1000genomes.org/
