# Genes and transcripts

Scout stores information about genes and transcripts. The information is collected from a couple of resources, these can be updated manually if desired. Definition of what genes that exists and their correct id and symbols are collected from [HGNC][hgnc]. Unfortunately HGNC does only maintain a distribution for GRCh38, at this time (mid 2018) there are many resources that lack support for build 38 so many investigators still use build 37. We therefore load two gene sets, one for each build.


## Genes with missing RefSeq transcripts

There is a issue where this problem is discussed [here][issue], please read that since it is important.
When we first look at all genes we could see the following:

`Nr of genes: 33578`
`Nr without transcripts: 11048`

So 1/3 of all genes are missing any refseq transcript. This came out as a high number at first, after some thought one might realise that many of these genes are not protein coding etc.

If we look at disease causing genes from OMIM there are 16 genes that are missing refseq id for any transcript in ensembl build 37, 7 genes in build 38.

The genes in OMIM without refseq transcripts in build 37 are the following:

```
TTC25
PTPRQ
SRD5A2
PIGY
FGF16
TRAC
PADI6
GDF1
TUBB3
IGHG2
IGHM
IGKC
FCGR2C
KMT2B
NEFL
NR2E3
```

In the gene panels there are one more gene outside OMIM wihtout refseq transcripts: `MAP3K14`

We will here look at all these genes in detail:

### TTC25

Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
--- | --- |--- | --- |  --- | ---
 37 | HG185_PATCH | ENSG00000260703 | TTC25 | ENST00000569427 | -
 37 | HG185_PATCH | ENSG00000260703 | TTC25 | ENST00000561994 | -
 37 | HG185_PATCH | ENSG00000260703 | TTC25 | ENST00000569541 | NM_031421
 37 | HG185_PATCH | ENSG00000260703 | TTC25 | ENST00000565052 | -
 37 | 17 | ENSG00000204815 | TTC25 | ENST00000593239 | -
 37 | 17 | ENSG00000204815 | TTC25 | ENST00000591658 | -
 37 | 17 | ENSG00000204815 | TTC25 | ENST00000585530 | -
 37 | 17 | ENSG00000204815 | TTC25 | ENST00000377540 | -
 --- | --- |--- | --- |  --- | ---
 38 | 17 | ENSG00000204815 | TTC25 | ENST00000593239 | -
 38 | 17 | ENSG00000204815 | TTC25 | ENST00000591658 | -
 38 | 17 | ENSG00000204815 | TTC25 | ENST00000377540 | NM_031421
 38 | 17 | ENSG00000204815 | TTC25 | ENST00000377540 | NM_031421
 38 | 17 | ENSG00000204815 | TTC25 | ENST00000585530 | -

### PTPRQ

Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
--- | --- |--- | --- |  --- | ---
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000551042 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000547376 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000551573 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000526956 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000547485 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000551624 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000547881 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000549355 | -
**37** | 12 | ENSG00000139304 | PTPRQ | ENST00000266688 | -
--- | --- |--- | --- |  --- | ---
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000623635 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000551042 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000547376 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000551573 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000614701 | NM_001145026
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000547485 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000551624 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000547881 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000549355 | -
**38** | 12 | ENSG00000139304 | PTPRQ | ENST00000616559 | XM_017019274

### SRD5A2

Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
--- | --- |--- | --- |  --- | ---
37 | 2 | ENSG00000049319 | SRD5A2 | ENST00000405650 | -
37 | 2 | ENSG00000049319 | SRD5A2 | ENST00000233139 | -
--- | --- |--- | --- |  --- | ---
38 | 2 | ENSG00000277893 | SRD5A2 | ENST00000622030 | NM_000348

Here we can see that two transcripts has been merged to one and been given a refseq identifier. Most probable one of the old transcripts match the new one. We can not be sure if variants are missed here.

### PIGY

Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
--- | --- |--- | --- |  --- | ---
37 | 4 | ENSG00000255072 | PIGY | ENST00000527353 | -
--- | --- |--- | --- |  --- | ---
38 | 4 | ENSG00000255072 | PIGY | ENST00000527353 | -

Here the transcript is identical for both builds so we dear to guess that we do not miss any variants.

### FGF16

Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
--- | --- |--- | --- |  --- | ---
 **37** | X | ENSG00000196468 | FGF16 | ENST00000439435 | -
 **37** | HG1426_PATCH | ENSG00000268853 | FGF16 | ENST00000600602 | -
--- | --- |--- | --- |  --- | ---
 **38** | X | ENSG00000196468 | FGF16 | ENST00000439435 | NM_003868

 The refseq transcript exists in build 37 but is missing the refseq identifier. We would NOT miss any variants here.

### TRAC

 Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
 --- | --- |--- | --- |  --- | ---
 37 | 14 | ENSG00000229164 | TRAC | ENST00000478163 | -
 --- | --- |--- | --- |  --- | ---
 38 | 14 | ENSG00000277734 | TRAC | ENST00000611116 | -

 Transcripts have different ENS ids in both builds but are most probably the same. No refseq identifier for any build.

### PADI6

 Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
 --- | --- |--- | --- |  --- | ---
 *37* | 1 | ENSG00000256049 | PADI6 | ENST00000434762 | -
 *37* | 1 | ENSG00000256049 | PADI6 | ENST00000358481 | -
 --- | --- |--- | --- |  --- | ---
 *38* | 1 | ENSG00000276747 | PADI6 | ENST00000619609 | NM_207421
 *38* | CHR_HG2095_PATCH | ENSG00000280949 | PADI6 | ENST00000625380 | NM_207421

 Unclear what happens here...

### GDF1

 Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
 --- | --- |--- | --- |  --- | ---
 **37** | 19 | ENSG00000130283 | GDF1 | ENST00000247005 | -
 --- | --- |--- | --- |  --- | ---
 **38** | 19 | ENSG00000130283 | GDF1 | ENST00000247005 | -

 Same transcripts, no refseq in both builds. No variants will be missed here

### TUBB3

 Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
 --- | --- |--- | --- |  --- | ---
 **37** | 16 | ENSG00000198211 | TUBB3 | ENST00000556922 | -
 --- | --- |--- | --- |  --- | ---
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000555810 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000554444 | NM_001197181
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000556565 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000315491 | NM_006086
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000553656 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000556536 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000554116 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000554927 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000557262 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000557490 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000555576 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000554336 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000555609 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000553967 | -
 **38** | 16 | ENSG00000258947 | TUBB3 | ENST00000625617 | -

This is very unclear, it goes from one to many transcripts between the builds. Hard to say if variants are missed here.

### IGHG2

 Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
 --- | --- |--- | --- |  --- | ---
 **37** | 14 | ENSG00000211893 | IGHG2 | ENST00000390545 | -
 **37** | HG1592_PATCH | | ENSG00000270895 | IGHG2 | ENST00000603473 | -
 --- | --- |--- | --- |  --- | ---
 **38** | CHR_HSCHR14_3_CTG1 | ENSG00000274497 | IGHG2 | ENST00000621803 | -
 **38** | 14 | ENSG00000211893 | IGHG2 | ENST00000641095 | -
 **38** | 14 | ENSG00000211893 | IGHG2 | ENST00000390545 | -

 No refseq in any build. Same transcripts in both builds except a new one in a patch. No variants would be missed here.


### IGHM

 Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
 --- | --- |--- | --- |  --- | ---
 **37** | 14 | ENSG00000211899 | IGHM | ENST00000390559 | -
 **37** | HG1592_PATCH | ENSG00000271541 | IGHM | ENST00000605693 | -
 --- | --- |--- | --- |  --- | ---
 **37** | CHR_HSCHR14_3_CTG1 | ENSG00000282657 | IGHM | ENST00000626472 | -
 **37** | 14 | ENSG00000211899 | IGHM | ENST00000637539 | -
 **37** | 14 | ENSG00000211899 | IGHM | ENST00000390559 | -

 Same as above, no variants missing here

### IGKC

  Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
  --- | --- |--- | --- |  --- | ---
 **37** | 2 | ENSG00000211592 | IGKC | ENST00000390237 | -
  --- | --- |--- | --- |  --- | ---
 **38** | 2 | ENSG00000211592 | IGKC | ENST00000390237 | -

 Same in both builds. No variants would be missing here

### FCGR2C

  Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
  --- | --- |--- | --- |  --- | ---
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000502411 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000496692 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000466542 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000465075 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000473530 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000473712 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000482226 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000467903 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000507374 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000508651 | -
 **37** | 1 | ENSG00000244682 | FCGR2C | ENST00000543859 | -
  --- | --- |--- | --- |  --- | ---
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000502411 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000496692 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000466542 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000465075 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000473530 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000473712 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000482226 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000467903 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000507374 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000508651 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000611236 | -
 **38** | 1 | ENSG00000244682 | FCGR2C | ENST00000543859 | NR_047648

Most probably no variants would be missing here. All transcripts seems to be correct between the builds.

### KMT2B

  Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
  --- | --- |--- | --- |  --- | ---
 **37** | 19 | ENSG00000105663 | KMT2B | ENST00000606995 | -
 **37** | 19 | ENSG00000105663 | KMT2B | ENST00000607650 | -
 **37** | 19 | ENSG00000105663 | KMT2B | ENST00000592092 | -
 **37** | 19 | ENSG00000105663 | KMT2B | ENST00000585476 | -
 **37** | 19 | ENSG00000105663 | KMT2B | ENST00000586308 | -
  --- | --- |--- | --- |  --- | ---
 **38** |19 | ENSG00000272333 | KMT2B | ENST00000420124 | NM_014727
 **38** |19 | ENSG00000272333 | KMT2B | ENST00000606995 | -
 **38** |19 | ENSG00000272333 | KMT2B | ENST00000592092 | -
 **38** |19 | ENSG00000272333 | KMT2B | ENST00000585476 | -
 **38** |19 | ENSG00000272333 | KMT2B | ENST00000586308 | -

Here the transcript `ENST00000607650` in build 37 have probably changed id to `ENST00000420124` and been given a refseq identifier.

### NEFL

  Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
  --- | --- |--- | --- |  --- | ---
 **37** | 8 | ENSG00000104725 | NEFL | ENST00000221169 | -
  --- | --- |--- | --- |  --- | ---
 **38** | 8 | ENSG00000277586 | NEFL | ENST00000610854 | NM_006158
 **38** | 8 | ENSG00000277586 | NEFL | ENST00000615973 | -
 **38** | 8 | ENSG00000277586 | NEFL | ENST00000639464 | -
 **38** | 8 | ENSG00000277586 | NEFL | ENST00000619417 | -

This is unclear, probably ENST00000221169 has been renamed to ENST00000610854 and been given a refseq identifier.

### NR2E3

  Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
  --- | --- |--- | --- |  --- | ---
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000561604 | -
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000567496 | -
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000562839 | -
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000562925 | -
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000563709 | -
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000398840 | -
 **37** | 15 | ENSG00000031544 | NR2E3 | ENST00000326995 | -
  --- | --- |--- | --- |  --- | ---
 **38** | 15 | ENSG00000278570 | NR2E3 | ENST00000621736 | -
 **38** | 15 | ENSG00000278570 | NR2E3 | ENST00000617575 | NM_014249
 **38** | 15 | ENSG00000278570 | NR2E3 | ENST00000621098 | NM_016346
 **38** | 15 | ENSG00000278570 | NR2E3 | ENST00000563709 | -

This is unclear. We might miss variants here

### MAP3K14

  Build | Chrom | EnsGeneID | Gene Name  | EnsTransID | RefSeq mRNA
  --- | --- |--- | --- |  --- | ---
 **37** | 17 | ENSG00000006062 | MAP3K14 | ENST00000587332 | -
 **37** | 17 | ENSG00000006062 | MAP3K14 | ENST00000592267 | -
 **37** | 17 | ENSG00000006062 | MAP3K14 | ENST00000586644 | -
 **37** | 17 | ENSG00000006062 | MAP3K14 | ENST00000344686 | -
 **37** | 17 | ENSG00000006062 | MAP3K14 | ENST00000376926 | -
  --- | --- |--- | --- |  --- | ---
 **38** | 17 | ENSG00000006062 | MAP3K14 | ENST00000344686 | NM_003954
 **38** | 17 | ENSG00000006062 | MAP3K14 | ENST00000640087 | -
 **38** | 17 | ENSG00000006062 | MAP3K14 | ENST00000592267 | -
 **38** | 17 | ENSG00000006062 | MAP3K14 | ENST00000586644 | -
 **38** | 17 | ENSG00000006062 | MAP3K14 | ENST00000617331 | -
 **38** | 17 | ENSG00000006062 | MAP3K14 | ENST00000376926 | -
 **38** | CHR_HSCHR17_2_CTG5 | ENSG00000282637 | MAP3K14 | ENST00000633437 | -
 **38** | CHR_HSCHR17_2_CTG5 | ENSG00000282637 | MAP3K14 | ENST00000634016 | -

 Here one of the transcripts have been given a refseq identifier in build 38, that transcript exists in build 37 so no variants would be missed here.

[hgnc]: https://www.genenames.org
[issue]: https://github.com/Clinical-Genomics/scout/issues/570
