# Genes, transcripts and exons

As described in the user guide, Scout creates it's own definition of genes and transcripts by connecting information from some different sources. In the world of bioinformatics information is often collected from a wide variety of sources that may be inconsistent. Therefore we try to create our own definitions as far as possible and then map the information back.
The base for gene information is collected from [HGNC][hgnc] since it is a well curated source of gene information.
Coordinates for genes, transcripts and exons are collected from [Ensembl biomart][biomart].
Links to disease phenotypes are collected from [OMIM][omim], incomplete penetrance information is collected from [HPO][hpo] and intolerance to variation (pLI-scores) from [ExAC][exac].


## Update genes and transcripts

To update the gene definitions use command

```bash
scout update genes
```

When running this command the latest version of all the above described sources is fetched and that database gets updated.


## Update/load exons

The exons are fetched from ensembl through the ensembl biomart. To load or update the exon information please run command

```bash
scout load exons
```
where you can specify what build to use, default is `37`.

There has been some problems to download from the ensembl biomart for build `38`, in this case one can download a flatfile from
the [ensembl martview][martview] and selecting:

- database: ensembl genes (current version)
- dataset: Human Genes (current version)
- Filters:
    - Region: Chromosomes/scaffold (Choose 1-22, X, Y and MT)
- Attributes:
    - Features: Unbox everything
    - Structures: GENE (Choose Gene stable ID, Transcript stable ID, Strand, 5'UTR start, 5'UTR end,
                        3'UTR start, 3'UTR end)
    - Structures: EXON (Choose Exon region start, Exon region end, Exon rank in transcript, Exon stable ID)

Download this file and use command
```
scout load exons --exons-file path/to/mart_export.txt --build 38
```


[martview]: https://www.ensembl.org/biomart/martview
[hgnc]: https://www.genenames.org
[biomart]: http://www.ensembl.org/biomart/martview/63a1d476e23a0672e6c89d0e80fb62b5
[omim]: https://omim.org
[hpo]: https://human-phenotype-ontology.github.io
[exac]: http://exac.broadinstitute.org/faq
