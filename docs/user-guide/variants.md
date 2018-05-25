## Variants
The big list of variants. This page serves as an overview of all data and annotations for a single case. It's meant to allow you to skim through many variants ordered by the ranking.

The first couple of columns are meant to give you a sense of place in the overall ranked list. The "Rank" column is especially useful after applying various filters.

Hovering over both "1000 Genomes" (frequency) and "CADD score" (severity) columns will reveal additional metrics in a popup.

Hovering over "Inheritance models" will pop up a list of all possible compounds if the variants follows this pattern.

At the bottom of the list you will find a button to load the next batch of variants in the list. To return to the previous batch of variants, just press the browser back button.

It's also possible to filter the variants using a number of different criteria. Open the filters panel by clicking the "filter" icon in the top right. Here you can fill in form and click "Filter variants" to update the list. This is also the place where you switch gene lists.

----------

## Variant
This is the most complex view with a lot of related data presented to the user in a compact way. A lot of thought went into the design of the layout so here it the imagined workflow.

### Toolbar
Two options are added to the right side of the menu:

  - Send Sanger email to an institute related email address.
  - Pin the current variant as interesting so that it shows up in the case view.
  - Mark variant as causative. This is only to be used when a variant is confirmed to be causative - it will set the case to "solved" automatically.

### Fixed header
Introduces the basic facts of the variant that the user is often referring back to. As an example you need to refer back to the chromosome when assessing possible inheritance models.

### Summary
This is the first a user looks at when assesing the variant.

  - Rank score/CADD score
  - Disease gene model, possible inheritance models, OMIM model
  - Frequencies
  - CLINSIG number

## Details

see [Annotations](annotations.md)

### Functional Annotation ###

This is the worst functional impact of all transcripts

### Clinvar submission of pinned variants ###

Single nucleotide variants, indels, insertions, as well as larger structural variants can be used to create submissions to [Clinvar][clinvar], a free public database of phenotype-genotype associations. One of more pinned variants for a case with assigned phenotype might be used from the Clinvar submission page to create comma separated file to be used in the submission process. The Scout submission form mirrors the fields on the Clinvar submission spreadsheets. Optional case data for one or more pinned variants can also be generated and uploaded together with the variants during the file submission. Prior registration of a user and a submitting organization to the Clinvar portal is required to submit data to the Clinvar database.

### Region Annotation ###

This is the region of the most severe functional impact

### GT Call

### Compounds
Only interesting when the compound inheritance pattern is required, the list can be very long - best to put it far down the page.

[clinvar]: https://www.ncbi.nlm.nih.gov/clinvar/
[markdown]: https://help.github.com/articles/markdown-basics/
