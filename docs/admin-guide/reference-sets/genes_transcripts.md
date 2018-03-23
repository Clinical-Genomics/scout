# Downloading resources to build reference sets

For all of the ensembl downloads we choose filters chr 1-22, X, Y, MT and only genes with hgnc identifier

## Ensembl genes

We collect coordinate infromation about genes from ensembl. There are two gene files, one for each build in `scout/resources` these are named `ensembl_genes_37.tsv.gz` and `ensembl_genes_38.tsv.gz`.

If for any reason an admin want to replace/update these files they are collected from ensembl BIOMART with the following choices made:

- Chromosome/scaffold name
- Gene stable ID
- Chromosome/scaffold name
- Gene start (bp)
- Gene end (bp)

from EXTERNAL:

- HGNC ID

The link between different resources are made via HGNC id which is the most stable gene identifier

## Ensembl transcripts

Same as above, we collect information about coordinates and refseq from ensembl. There are two files here as well: `ensembl_transcripts_37.tsv.gz` and `ensembl_transcripts_38.tsv.gz`.

Those are collected by choosing the following information:

- Chromosome/scaffold name
- Gene stable ID
- Transcript stable ID
- Transcript start (bp)
- Transcript end (bp)

from EXTERNAL:

- RefSeq mRNA ID
- RefSeq mRNA predicted ID
- RefSeq ncRNA ID

## Ensembl exons
Choose **attributes** then **structures**.
Under **GENE** choose:

- Chromosome/scaffold name
- Gene stable ID
- Transcript stable ID
- Strand
- 5' UTR start
- 5' UTR end
- 3' UTR start
- 3' UTR end

Under **EXON** choose:

- Exon region start (bp)
- Exon region start (bp)
- Exon rank in transcript

Under **FILTERS**/**Gene** choose

- Limit to genes with HGNC Symbol ID(s)

click **results** and then download

## Ensembl genes and transcripts

Choose **attributes** then **structures**.
Under **GENE** choose:

- Chromosome/scaffold name
- Gene stable ID
- Transcript stable ID
- Gene start (bp)
- Gene end (bp)
- Transcript start (bp)
- Transcript end (bp)
- Gene name

Under **EXTERNAL** the **External References** choose:

- RefSeq mRNA ID
- RefSeq mRNA predicted ID
- RefSeq ncRNA ID

Under **FILTERS**/**Gene** choose

- Limit to genes with HGNC Symbol ID(s)

click **results** and then download

