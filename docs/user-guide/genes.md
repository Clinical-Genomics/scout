# Genes and transcripts

Scout stores information about genes and transcripts. The information is collected from a couple of resources, these can be updated manually if desired. Defenition of what genes that exists and their correct names are collected from [HGNC][hgnc]. Unfortunately HGNC does only maintain a distribution for GRCh38, at this time (mid 2017) there are many resorces that lack support for build 38 so many investigators still use build 37. We then use two files, one for each build, with information about coordinates and transcripts from ensembl. These files together make up the defenition of genes that are used in scout.


[hgnc]: http://www.genenames.org