## IGV browser settings

### Default tracks

The default file formats for viewing alignments in Scout is [BAM][bam] or [CRAM][cram]. Scout utilizes the embeddable interactive genome visualization tool [igv.js][igv] to display sample tracks and the following default tracks, available in the IGV browser by default for both genome builds GRCh37 (hg19) and GRCh38 (hg38):

- Reference genome track
- Genes track
- ClinVar SNVs track
- ClinVar CNVs track

Reference genome and genes track are collected from the [Broad Institute Amazon S3 storage][amazon_s3], with the exception of old hg19 1kg references, which are served from a JP mirror. The ClinVar tracks are available from the UCSC Genomics Institute [Sequence and Annotation Downloads][ucsc_downloads]

### Custom reference tracks

It is possible to add custom reference tracks to the IGV browser in Scout. This is done by adding a `CUSTOM_REFERENCE` dictionary to the Scout configuration file, with the following structure:

```python
# Custom IGV.js reference tracks: use a local mirror for the most part
CUSTOM_REFERENCE = {
    "37": {
        "id": "hg19",
        "name": "GRCh37 1kg decoy",
        "fastaURL": "/home/proj/production/scout_igv_tracks/seq/grch37_homo_sapiens_-d5-.fasta",
        "indexURL": "/home/proj/production/scout_igv_tracks/seq/grch37_homo_sapiens_-d5-.fasta.fai",
        "cytobandURL": "/home/proj/production/scout_igv_tracks/seq/cytoBand.txt.gz",
        "aliasURL": "https://raw.githubusercontent.com/igvteam/igv-data/refs/heads/main/data/hg19/hg19_alias.tab",
    },
    "38": {
        "id": "hg38",
        "name": "GRCh38",
        "fastaURL": "/home/proj/production/scout_igv_tracks/seq/grch38_homo_sapiens_-assembly-.fasta",
        "indexURL": "/home/proj/production/scout_igv_tracks/seq/grch38_homo_sapiens_-assembly-.fasta.fai",
        "cytobandURL": "/home/proj/production/scout_igv_tracks/seq/cytoBand.txt.gz",
        "aliasURL": "https://raw.githubusercontent.com/igvteam/igv-data/refs/heads/main/data/hg38/hg38_alias.tab",
        "chromosomeOrder": "chr1, chr2, chr3, chr4, chr5, chr6, chr7, chr8, chr9, chr10, chr11, chr12, chr13, chr14, chr15, chr16, chr17, chr18, chr19, chr20, chr21, chr22, chrX, chrY, chrM",
    },
}
```
It is possible to locally mirror only some of the files, and give URLs for others, but if you do add any `CUSTOM_REFERENCE` you will need to supply locations for all the keys as the default references will no longer be configured.

### Custom tracks

One or more custom tracks could be additionally loaded and visualized in the Scout IGV browser by including them in the general Scout configuration file.
To add a public track of [type "variant"][igv_variant_track] to Scout use the following example line:
```
CLOUD_IGV_TRACKS = [
    {
        "name": "custom_public_bucket",
        "access": "public",
        "tracks": [
            {
                "name": "Display name of track",
                "type": "variant",
                "format": "vcf",
                "build": "37", # or "38"
                "url": "url_to_resource",
                "indexURL": "url_to_resource_index",
            }
        ],
    },
]
```


[bam]: https://software.broadinstitute.org/software/igv/BAM
[cram]: https://software.broadinstitute.org/software/igv/FileFormats/CRAM
[igv]: https://github.com/igvteam/igv.js
[amazon_s3]: https://s3.amazonaws.com/igv.broadinstitute.org
[ucsc_downloads]: https://hgdownload.soe.ucsc.edu/downloads.html
[igv_variant_track]: https://github.com/igvteam/igv.js/wiki/Variant-Track
