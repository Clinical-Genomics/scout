# Genes and transcripts

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




[hgnc]: www.genenames.org
[biomart]: http://www.ensembl.org/biomart/martview/63a1d476e23a0672e6c89d0e80fb62b5
[omim]: https://omim.org
[hpo]: https://human-phenotype-ontology.github.io
[exac]: http://exac.broadinstitute.org/faq