## What's new in 4.116?

*Posted: Nov 5 2026*

🍁 Scout 4.116 is here! 🍁 This release adds new resources and scores for variant interpretation, improves repeat-expansion workflows, and brings useful updates to ClinVar submissions, ACMG classification, and variant browsing.

### Highlights

* **More information for variant interpretation.** Scout now parses and displays **AlphaGenome Variant Impact (AVI)** and **AlphaMissense** scores. For hg38 variants, you can also follow links to **dbNSFP** and **gnomAD long-read sequencing (LRS)**. New gnomAD frequency fields include WES, homozygous alternate counts, and allele counts, with more significant digits for frequency values.

* **Improved STR workflows.** STR variants now link to **STRchive**. Custom images can also be matched to both STR repetitions (REPID) and tandem repeat IDs (TRID), so matching images can be discovered and associated with the corresponding variants.

* **More detail in ACMG classification.** The ACMG classification form now shows the Bayesian point contribution for each criterion, making the contribution of individual criteria easier to review.

* **More control over ClinVar submissions.** ClinVar submissions can once again be deleted from the ClinVar portal through the API.

### Also included

* Variants with duplicate IDs in a loading batch now retain the highest-scoring variant.
* Links from the Dark Regions page to SNVs and SVs are no longer restricted by the gene panels selected on that page.
* Dark Regions and SMN have been moved to a separate blueprint.
* Non-numeric SuperDups fraction match annotations no longer prevent variant loading.
* STR genotype depth parsing and parsing of unexpectedly haploid genotype arrays have been fixed.
* STR variants with identical sort keys are now returned consistently, preventing variants from being missed during pagination.
* Documentation now covers external services accessed by a Scout installation, the README overview and supported-pipeline FAQ link have been updated, and automation is now available for building and uploading a stage-branch CLI Docker image.
