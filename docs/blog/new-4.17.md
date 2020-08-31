## What's new in 4.17? 🍁

_Posted: 3 Jun 2020_

Minor release 4.17 and its patch (4.17.1) introduce the following new features/bugfixes:

## New features

- COSMIC badge shown in cancer variants
- Default gene-panel in non-cancer structural view in url (thanks @ViktorHy)
- Filter SNVs and SVs by cytoband coordinates (read [ here ](#cytobands) how to enable the functionality)
- Filter cancer SNV variants by alt allele frequency in tumor
- Correct genome build in UCSC link from structural variant page (much appreciated @ViktorHy)

## Bugfixes

- Bug in clinVar form when variant has no gene
- Bug when sharing cases with the same institute twice
- Page crashing when removing causative variant tag
- Do not default to GATK caller when no caller info is provided for cancer SNVs


<a name="cytobands"></a>
### Loading chromosome cytobands to use them in variant filtering
Cytoband files for genome builds GRCh37 and GRCh38 (37 and and 38 in Scout) are provided in resources folder.
In order to use cytoband filtering in variants (SNV/Indels or structural variants), cytoband coordinates should be loaded to Scout database

Cytoband database collection is automatically populated when a new Scout setup is initiated using the command:
```
scout setup database

```

To load cytobands in a Scout database already containing data, from the command line simply type:
```
scout load cytobands
```
