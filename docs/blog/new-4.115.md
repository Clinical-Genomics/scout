## What's new in 4.115?

*Posted: Sep 28 2026*

Scout 4.115 is here! 🎉 This release brings a major update to the ClinVar germline submission workflow, a new way of exploring genomic regions, and several improvements to variant interpretation, reporting, and the Scout user interface.

### Highlights

* **A new region view — and new dosage sensitivity regions!** 🧬 Scout can now display genomic regions directly. We have also added **ClinGen dosage sensitivity data**, including [ISCA regions](https://search.clinicalgenome.org/kb/gene-dosage?page=1&size=25&search=), to the database. These regions can be explored in Scout and **added to gene panels**, by editing genes present in the panel.

* **ClinVar germline submissions have moved to the new API format.** Germline submissions are now handled using the new `germlineSubmission` format introduced by the [ClinVar API](https://www.ncbi.nlm.nih.gov/clinvar/docs/api_http/). Old-format germline submissions are automatically deprecated. They will remain available for viewing in Scout, but can no longer be submitted to ClinVar. New germline submissions can be created using the updated workflow. The submission pages have also received several usability improvements, including clearer test-endpoint buttons, better condition handling, and variant and case IDs throughout the multistep form.

* **Easier ClinVar submission searches.** ClinVar submissions can now be filtered by **gene**, and oncogenicity submissions can also be searched by **ClinVar ID**, making it easier to find the submission you're looking for.

* **More detailed VUS classification.** ClinVar germline submissions now support three additional VUS terms: **VUS-high, VUS-mid and VUS-low**.

* **More genomic context with AlphaGenome Atlas.** Links to the AlphaGenome Atlas have been added, giving you another way to explore the genomic context around variants.

* **More ACMG information in Scout.** The variant page now shows the **ACMG Bayesian classification** based on [Tavtigian et al.](https://pubmed.ncbi.nlm.nih.gov/29300386/), and ACMG criterion details are included in the case general report.

### Also included

* The **Sex** column is now shown in the samples table for cancer cases.
* The Gens viewer for a case now opens in a new tab.
* Rank scores can be displayed for cancer SVs.
* An **Oncoanalyser Orange report** can be added to an existing case through the CLI or when loading a case.
* The Sanger verification button now changes color according to its verification status.
* gnomAD constraint data has been updated to v4.1.1.
* IGV.js has been updated to 3.8.9, including a fix for a rare issue with TLEN colouring.
* Links and the ClinVar multistep submission form are now easier to see in dark mode.
* MT/M variants now automatically use genome build 38 when determining their variant locus.

