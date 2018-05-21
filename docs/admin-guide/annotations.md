# Annotations

Scout is a primarily a visualisation tool with some other functionality. One could imagine that in the future, some or all annotations could be performed by Scout. For now scout will look for some known keys when uploading a VCF and extract information for those. [VEP][vep] is the tool supported for functional and regional annotations at the moment, [SnpEff][snpeff] will be added in the near future. For the other types of annotations Scout will look for certain keys in the INFO field of the vcf and expect the value to be of a specific type. This means that there is not a dependency on any other specific annotation tool besides VEP, just make sure that the key and values are correct according to the specification below.

### Rank score

One of the hard problem when dealing with whole genome data is the huge amount variants that are generated in every analysis. Scout was developed to be used in rare variant analysis, this means that there is ony a small number of variants that are actually interesting to look at. We do not want to store all variants from each case in a database that should be able to controll thousands of cases. To solve this problem we are working with rank scores, each variant is scored according to a scoring schema then we only upload and sort the variants based on their rank score. In this way the users can start by looking at the variants that looks potentially most dangerous from a bioinformatic perspective. We use the tool [genmod][genmod] to (among other things) score the variant, but as long as there is a `RankScore`-field in the `INFO` field of the VCF with a float as value it is handeled by Scout.

## Annotation keys and tool suggestions

In this section all the different annotation keys and suggestions of tools that can be used to annotate them are listed.

### Frequencies 

#### Gnomad ####

The frequency from the [1000G][1000g] population database.

- Key: `GNOMADAF`
- Value: `Float`
- Tools: [VEP][vep], [SnpEff][snpeff], [vcfanno][vcfanno]

#### GNOMADAF_POPMAX ####

Maximum Allele Frequency across populations

- Key: `GNOMADAF_POPMAX`
- Value: `Float`
- Tools: [VEP][vep], [SnpEff][snpeff], [vcfanno][vcfanno]

#### 1000G ####

The frequency from the [1000G][1000g] population database.

- Key: `1000GAF`
- Value: `Float`
- Tools: [VEP][vep], [SnpEff][snpeff], [genmod][genmod], [vcfanno][vcfanno]

#### 1000G_MAX_AF ####

The maximum allele frequency of all populations in the [1000G][1000g] population database.

- Key: `1000G_MAX_AF`
- Value: `Float`
- Tools: custom made, we have modified the 1000G file and use [genmod][genmod]

#### ExAC ####

The frequency from the [ExAC][exac] population database.

- Key: `EXACAF`
- Value: `Float`
- Tools: [VEP][vep], [SnpEff][snpeff], [genmod][genmod], [vcfanno][vcfanno] 


#### ExAC_MAX_AF ####

The maximum allele frequency of all populations [ExAC][exac] population database. 

- Key: `EXAC_MAX_AF`
- Value: `Float`
- Tools: custom made, we have modified the exac file and use [genmod][genmod]

#### SWEREF ####

The frequency from the [SWEREF][SWEREF] population database.

- Key: `SWEREFAF`
- Value: `Float`
- Tools: [SnpEff][snpeff]

#### MTAF ####

The frequency for the Mitochondria from MitoMap.

- Key: `MTAF`
- Value: `Float`
- Tools: [SnpEff][snpeff]

### Clinvar ###

#### CLNREVSTAT ####

ClinVar review status for the Variation ID.

- Key: `CLNREVSTAT`
- Value: `String`
- Tools: [VEP][vep], [SnpEff][snpeff]

#### CLNSIG ####

Clinical significance for this single variant.

- Key: `CLNSIG`
- Value: `String`
- Tools: [VEP][vep], [SnpEff][snpeff]

#### CLNVID ####

ClinVar Variation ID.

- Key: `CLNVID`
- Value: `Integer`
- Tools: [VEP][vep], [SnpEff][snpeff]
- Comment: MIP preprocessed file

### VEP ###

VEP description of vcf annotations.

- Key: `CSQ`
- Sub_key: `Allele|Consequence|IMPACT|SYMBOL|Gene|Feature_type|Feature|BIOTYPE|EXON|INTRON|HGVSc|HGVSp|cDNA_position|CDS_position|Protein_position|Amino_acids|Codons|Existing_variation|DISTANCE|STRAND|FLAGS|SYMBOL_SOURCE|HGNC_ID|CANONICAL|TSL|APPRIS|CCDS|ENSP|SWISSPROT|TREMBL|UNIPARC|SIFT|PolyPhen|DOMAINS|HGVS_OFFSET|MOTIF_NAME|MOTIF_POS|HIGH_INF_POS|MOTIF_SCORE_CHANGE|LoFtool|MaxEntScan_alt|MaxEntScan_diff|MaxEntScan_ref`
- Value: `String`
- Tools: [VEP][vep]

### VT ###

#### OLD_MULTIALLELIC ####

Decompose key with original inforamtion.

- Key: `OLD_MULTIALLELIC`
- Value: `String`
- Tools: [vt][vt]

#### OLD_VARIANT ####

Normalize key with original information.

- Key: `OLD_VARIANT`
- Value: `String`
- Tools: [vt][vt]

### Severity ###

#### CADD score ####

The Combined Annotation Dependent Depletion([CADD][cadd]) score. A prediction of the deleterioussness for a variant.

- Key: `CADD` or `cadd` in VEP `CSQ` field
- Value: `Float`
- Tools: [VEP][vep], [SnpEff][snpeff], [genmod][genmod], [vcfanno][vcfanno] 

#### SIFT ####

The [SIFT][sift]) prediction for how a variation affects the protein.

- Key: `CSQ`-`SIFT`
- Value: `String`
- Tools: [VEP][vep]

#### PolyPhen ####

The [PolyPhen][polyphen]) prediction for how a variation affects the protein.

- Key: `CSQ`-`PolyPhen`
- Value: `String`
- Tools: [VEP][vep]

#### Spidex ####

Splicing annotation

- Key: `SPIDEX`
- Value: `Float`
- Tools: [SnpEff][snpeff]

#### Rank score ####

##### ModelScore #####

PHRED score for genotype models.

- Key: `ModelScore`
- Value: `Float`
- Tools: [genmod][genmod]

##### RankResult #####

Genmod description of rank score results.

- Key: `RankResult`
- Value: `String`
- Tools: [genmod][genmod]

##### RankScore #####

The combined rank score for a variant

- Key: `RankScore`
- Value: `Float`
- Tools: [genmod][genmod]

### Conservation ###

#### Gerp ####

The Genomic Evolutionary Rate Profiling([GERP][gerp]) conservation string. An estimation of how conserved this position is.

#### GERP++_NR ####

- Key: `dbNSFP_GERP___NR`
- Value: `String`
- Tools: [SnpSift][snpsift]

#### GERP++_RS ####

- Key: `dbNSFP_GERP___RS`
- Value: `String`
- Tools: [SnpSift][snpsift]

#### phastCons ####

The [PHASTcons][phastcons] conservation string.

- Key: `dbNSFP_phastCons100way_vertebrate`
- Value: `String`
- Tools: [SnpSift][snpsift]

#### phylop ####

The [phylop][phylop] 100 way predicted conservation string.

- Key: `dbNSFP_phyloP100way_vertebrate`
- Value: `String`
- Tools: [SnpSift][snpsift]

### Inheritance ###

#### Genetic models ####
What genetics models are followed for the variant in the particular family

- Key: `GeneticModels`
- Value: list of `String`
- Tools: [genmod][genmod]

#### Autosomal Recessive Compounds ####
What variants is this variant in Autosomal Recessive Compound with?

- Key: `Compounds`
- Value: list of `String`
- Tools: [genmod][genmod]

### Autozygosity ###

#### Rhocall ####

#### AZ #####

Autozygous positon call.

- Key: `AZ`
- Value: Flag
- Tools: [rhocall][rhocall]

#### AZLENGTH ####

Autozygous region length.

- Key: `AZLENGTH`
- Value: String
- Tools: [rhocall][rhocall]

#### AZQUAL ####

Autozygous positon call quality.

- Key: `AZQUAL`
- Value: String
- Tools: [rhocall][rhocall]

#### AZTYPE ####

Autozygous region type.

- Key: `AZTYPE`
- Value: String
- Tools: [rhocall][rhocall]

#### GATK ####

Source vcf for the merged vcf record.

- Key: `set`
- Value: String
- Tools: [gatk][gatk]

[vep]: http://www.ensembl.org/info/docs/tools/vep/index.html
[snpeff]: http://snpeff.sourceforge.net/about.html
[genmod]: https://github.com/moonso/genmod
[vcfanno]: https://github.com/brentp/vcfanno
[snpsift]: http://snpeff.sourceforge.net/SnpSift.html

[1000g]: http://www.1000genomes.org/
[exac]: http://exac.broadinstitute.org
[SWEREF]: https://swefreq.nbis.se/
[vt]: https://github.com/atks/vt
[cadd]: http://cadd.gs.washington.edu
[gerp]: http://mendel.stanford.edu/SidowLab/downloads/gerp/index.html
[phastcons]: http://compgen.cshl.edu/phast/
[phylop]: http://genome.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=cons100way
[sift]: http://sift.jcvi.org
[polyphen]: http://genetics.bwh.harvard.edu/pph2/dokuwiki/
[rhocall]: https://github.com/dnil/rhocall
[gatk]: https://software.broadinstitute.org/gatk/
