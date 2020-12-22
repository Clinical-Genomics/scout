## IGV browser settings

### Default tracks

The default file formats for viewing alignments in Scout is [BAM][bam] or [CRAM][cram]. Scout utilizes the embeddable interactive genome visualization tool [igv.js][igv] to display sample tracks and the following default tracks, available in the IGV browser by default for both genome builds GRCh37 (hg19) and GRCh38 (hg38):

- Reference genome track
- Genes track
- ClinVar SNVs track
- ClinVar CNVs track

Reference genome and genes track are collected from the [Broad Institute Amazon S3 storage][amazon_s3], while the ClinVar tracks are available in the UCSC Genomics Institute [Sequence and Annotation Downloads][ucsc_downloads]


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
