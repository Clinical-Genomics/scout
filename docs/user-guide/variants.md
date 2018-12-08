## Variants
The big list of variants. This page serves as an overview of all data and annotations for a single case. It's meant to allow you to skim through many variants ordered by the ranking.

The first couple of columns are meant to give you a sense of place in the overall ranked list. The "Rank" column is especially useful after applying various filters.

Hovering over both "1000 Genomes" (frequency) and "CADD score" (severity) columns will reveal additional metrics in a popup.

Hovering over "Inheritance models" will pop up a list of all possible compounds if the variants follows this pattern.

At the bottom of the list you will find a button to load the next batch of variants in the list. To return to the previous batch of variants, just press the browser back button.

It's also possible to filter the variants using a number of different criteria. Open the filters panel by clicking the "filter" icon in the top right. Here you can fill in form and click "Filter variants" to update the list. This is also the place where you switch gene lists.

----------

## Variant
This is the most complex view with a lot of related data presented to the user in a compact way. A lot of thought went into the design of the layout so here it the imagined workflow.

### Toolbar
Two options are added to the right side of the menu:

  - Send Sanger email to an institute related email address.
  - Pin the current variant as interesting so that it shows up in the case view.
  - Mark variant as causative. This is only to be used when a variant is confirmed to be causative - it will set the case to "solved" automatically.

### Fixed header
Introduces the basic facts of the variant that the user is often referring back to. As an example you need to refer back to the chromosome when assessing possible inheritance models.

### Summary
This is the first a user looks at when assesing the variant.

  - Rank score/CADD score
  - Disease gene model, possible inheritance models, OMIM model
  - Frequencies
  - CLINSIG number

#### SV frequency - SVDB
     Structural variant database freqency is annotated with [SVDB](https://github.com/J35P312/SVDB), using a clustering algorithm [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN). Variant type and chromosome are exact, but start and end positions for matches are approximate, and depend on previous cases from the database. In a region with multiple, inexactly positioned events, matching will be more relaxed than if only tightly clustered variants with near similar start and end coordinates have been found. Databases include research cases from Clinical genetics (WGS at NGI), clinical cases with arrayCGH (benign or pathogenic collections), Decipher, SweGen and local cases.

## Details

see [Annotations](annotations.md)

### Functional Annotation ###

This is the worst functional impact of all transcripts

### Clinvar submission of pinned variants ###

Single nucleotide variants, indels, insertions, as well as larger structural variants can be used to create submissions to [Clinvar][clinvar], a free public database of phenotype-genotype associations. One of more pinned variants for a case with assigned phenotype might be used from the Clinvar submission page to create comma separated file to be used in the submission process. The Scout submission form mirrors the fields on the Clinvar submission spreadsheets. Optional case data for one or more pinned variants can also be generated and uploaded together with the variants during the file submission. Prior registration of a user and a submitting organization to the Clinvar portal is required to submit data to the Clinvar database.

### Region Annotation ###

This is the region of the most severe functional impact

### GT Call

### Variant Callers
Badges below the GT Call table show the variant caller responsible for the calls and their filter status.
A variant with Pass status passed all the filters from its variant callers, whereas a Filtered call was detected by the caller but not deemed passing filter quality.

#### SNVs and indels

##### GATK
##### FreeBayes
##### SAMtools

#### SVs

SVs are structural variants, balanced or unbalanced chromosomal abberrations.
Size filtering can be done either to show only variants longer than the given size, or shorter if the "Length shorter than" checkbox is activated.
When the checkbox is ticked, queries are also inclusive of non-existing annotations e.g. SV events without size. Note that some BNDs, like interchromosomal translocations are given with a very large (larger than chromosome) size instead.

Scout supports viewing general SVs as encoded in the VCF format specification.
Some sample callers that we have worked with include:

##### TIDDIT
[TIDDIT](https://github.com/SciLifeLab/TIDDIT) Locally developed structural variant caller that uses discordant read pair detection and supplementary alignments for split reads from the bam file to call structural variations, including deletions, duplications, inversions and translocations (BND). The number of supporting links is used to call the reliability of the call. Read depth information is used to infer the variant type as well as zygosity where possible. Delivers exact breakpoints when possible. Sensitivity for clinically relevant deletions is 100%, balanced events lower but at a best-in-class >80%. Be advised to consider zygosity calls from balanced events as highly uncertain.

Jesper Eisfeldt, Francesco Vezzi, Pall Olason, Daniel Nilsson, Anna Lindstrand
[TIDDIT, an efficient and comprehensive structural variant caller for massive parallel sequencing data](https://f1000research.com/articles/6-664/v2)
F1000Research 2017, 6:664

##### CNVnator
[CNVnator](https://github.com/abyzovlab/CNVnator) Well established read depth aware CNV caller. Infers deletions and duplications from binning read depth. Will call inexact boundaries for the events. Effectively 100% sensitivity for large CNVs in accessible regions. Be wary if CNVnator did not call your large unbalanced variant - that may indicate a false positive. Comparatively decent zygosity-calls from v0.3.3.

Abyzov A, Urban AE, Snyder M, Gerstein M.
[CNVnator: an approach to discover, genotype, and characterize typical and atypical CNVs from family and population genome sequencing.](https://www.ncbi.nlm.nih.gov/pubmed/21324876) Genome Res. 2011 Jun;21(6):974-84.

##### Manta
[Manta](https://github.com/Illumina/manta): Internationally well used de-facto standard for structural variant calling. Uses discordant read pairs and split read graphs to call variants. Comparatively good sensitivity for insertions. Specificity is not always optimal. Be adviced of potential false positive calls of long range connectivity, in particular when in conflict with callers that rely more on read-depth.

Chen, X. et al. (2016) [Manta: rapid detection of structural variants and indels for germline and cancer sequencing applications.](doi:10.1093/bioinformatics/btv710) Bioinformatics, 32, 1220-1222. Be advised to consider zygosity calls from balanced events as uncertain.

##### Delly
[Delly](https://github.com/dellytools/delly)
The long standing, well known and decently performing tool Delly uses discordant read-pairs and split reads to call structural variants. Calls made are reliable from >300bp, but also sports an effective indel detection mode for sub-readlength indels. As with manta, Specificity is not always optimal. Be adviced of potential false positive calls of long range connectivity, in particular when in conflict with callers that rely more on read-depth. Be advised to consider zygosity calls as uncertain.

Tobias Rausch, Thomas Zichner, Andreas Schlattl, Adrian M. Stuetz, Vladimir Benes, Jan O. Korbel.
[Delly: structural variant discovery by integrated paired-end and split-read analysis.](https://academic.oup.com/bioinformatics/article/28/18/i333/245403)
Bioinformatics 2012 28: i333-i339.

#### STRs
Scout supports viewing STRs, Short Tandem Repeats, initially only for a clinical panel.

Tested callers include:

##### ExpansionHunter
[ExpansionHunter][expansion-hunter] Longer-than-readlength analysis of STR sites. Requires a pre-made panel file noting the location of target sites to analyze, then rapidly analyses bam files. Dolzenko et al [Detection of long repeat expansions from PCR-free whole-genome sequence data](https://genome.cshlp.org/content/27/11/1895).

##### Annotating STRs

The out put files of expansion hunter if preferably annotated with [stranger][stranger] before loaded into scout.

### Compounds (top 20)
Only interesting when the compound inheritance pattern is required, the list can be very long but is by default cropped to the top 20 highest ranked ones as shown in the heading.

[clinvar]: https://www.ncbi.nlm.nih.gov/clinvar/
[markdown]: https://help.github.com/articles/markdown-basics/
[expansion-hunter]: https://github.com/Illumina/ExpansionHunter
[stranger]: https://github.com/moonso/stranger
