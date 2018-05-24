# Annotations

This page will describe what is displayed in scout, what the different annotations mean and how they are parsed from the vcf file.

## Frequencies

### 1000G ###

The frequency from the [1000G][1000g] population database.

### 1000G_MAX_AF ###

The maximum allele frequency of all populations in the [1000G][1000g] population database.

### ExAC ###

The frequency from the [ExAC][exac] population database.

### ExAC_MAX_AF ###

The maximum allele frequency of all populations [ExAC][exac] population database. 

## Severity ##

### CADD score ###

The Combined Annotation Dependent Depletion([CADD][cadd]) score. A prediction of the deleterioussness for a variant.

### SIFT ###

The [SIFT][sift]) prediction for how a variation affects the protein.

### PolyPhen ###

The [PolyPhen][polyphen]) prediction for how a variation affects the protein.

## Conservation ##

### Gerp ###

The Genomic Evolutionary Rate Profiling([GERP][gerp]) conservation string. An estimation of how conserved this position is.

### phastCons ###

The [PHASTcons][phastcons] conservation string.

### phylop ###

The [phylop][phylop] 100 way predicted conservation string.

## External ID

### COSMIC

A matching exact CHROM, POS, REF, ALT from vcf with Catalogue Of Somatic Mutations In Cancer ([COSMIC][cosmic]). A link
to COSMIC if _a_ matching COSMIC variant is found.

[1000g]: http://www.1000genomes.org/
[cadd]: http://cadd.gs.washington.edu
[cosmic]: https://cancer.sanger.ac.uk/cosmic
[exac]: http://exac.broadinstitute.org
[gerp]: http://mendel.stanford.edu/SidowLab/downloads/gerp/index.html
[phastcons]: http://compgen.cshl.edu/phast/
[phylop]: http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=cons100way
[polyphen]: http://genetics.bwh.harvard.edu/pph2/dokuwiki/
[sift]: http://sift.jcvi.org
