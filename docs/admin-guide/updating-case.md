# Updating an existing case using the command line interface

A case in the scout db can be updated after loading. Best practica involves making a new scout load config,
and proceeding to upload with `scout load case -u my_new_config.yaml`, but occasionally a specific attribute can
be altered instead with the `scout update case` command.

```
Usage: scout update case [OPTIONS] [CASE_ID]

  Update a case in the database

Options:
  -n, --case-name TEXT           Search case by display name (institute ID
                                 should also be provided)
  -i, --institute TEXT           Case institute ID (case display name should
                                 also be provided)
  -c, --collaborator TEXT        Add a collaborator to the case
  --fraser TEXT                  Path to clinical WTS OMICS outlier FRASER TSV
                                 file to be added - NB variants are NOT loaded
  --outrider TEXT                Path to clinical WTS OMICS outlier OUTRIDER
                                 TSV file to be added - NB variants are NOT
                                 loaded
  --rna-genome-build [37|38]     RNA human genome build - should match RNA
                                 alignment files and IGV tracks
  --vcf PATH                     Path to clinical VCF file to be added - NB
                                 variants are NOT loaded
  --vcf-sv PATH                  path to clinical SV VCF file to be added
  --vcf-str PATH                 Path to clinical STR VCF file to be added -
                                 NB variants are NOT loaded
  --vcf-cancer PATH              Path to clinical cancer VCF file to be added
                                 - NB variants are NOT loaded
  --vcf-cancer-sv PATH           Path to clinical cancer structural VCF file
                                 to be added - NB variants are NOT loaded
  --vcf-research PATH            Path to research VCF file to be added - NB
                                 variants are NOT loaded
  --vcf-sv-research PATH         Path to research VCF with SV variants to be
                                 added
  --vcf-cancer-research PATH     Path to research VCF with cancer variants to
                                 be added - NB variants are NOT loaded
  --vcf-cancer-sv-research PATH  Path to research VCF with cancer structural
                                 variants to be added - NB variants are NOT
                                 loaded
  --vcf-mei PATH                 Path to clinical mei variants to be added -
                                 NB variants are NOT loaded
  --vcf-mei-research PATH        Path to research mei variants to be added -
                                 NB variants are NOT loaded
  --reupload-sv                  Remove all SVs and re upload from existing
                                 files
  --rankscore-treshold TEXT      Set a new rank score treshold if desired
  --sv-rankmodel-version TEXT    Update the SV rank model version
  --help                         Show this message and exit.
 ```
