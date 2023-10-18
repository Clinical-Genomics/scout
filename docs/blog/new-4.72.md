## What's new in 4.72?

_Posted: October 17 2023_

This crisp early autumn release contains some speedup to the case view (thank you @alkc) and case general report. There are also a few updates
to variant loading, refactoring for library updates and to allow it small but important changes to the case load config file, especially if
you use Custom case images.

### Variant loading and event index update
Previous cases matching causative variants are now forced to load for new cases, regardless of the score threshold,
much like Managed Variants and ClinVar P/LP/Conflicting annotated variants. To make this reasonalby fast we introduce
a new event index.

*Scout admins!* After installing the 4.72 update, update indices on the event collection:
```
scout index --update -c event
```
### Updated dependency requirements

We have refactored a bit to avoid deprecated functionality, and are so unfreezeing a few dependencies,
in particular pydantic and pymongo. If you deploy using docker, this should be a smooth ride. The same for
bare metal, just remember to `pip install -U -r requirements.txt`.

### Case load configuration file changes

#### Custom images

In response to a request from the Clinical Genomics facility in Lund, we have made adjustments to the keywords used for linking custom images to either the case page or a variant page.
Specifically, we have replaced the previous keywords 'case' and 'str' found in the case config file with more descriptive and user-friendly terms: 'case_images' and 'str_variants_images'.

Compatibility implications:
- Cases loaded with old keywords will keep displaying images as before
- All new cases uploaded are expected to use the new keywords in their config files
- Old cases configuration files will cease to work, and you'd need to switch to the new keywords in order to perform a case upload

#### Genome build check

We have updated the validation process for case configuration files to now require a mandatory entry for the genome build. You can specify the genome build for case analysis using either the 'genome_build' or 'human_genome_build' keyword,
with the accepted values included in this list: 37, 38, '37', '38'. While 'GRCh37' and 'GRCh38' genome build values will be accepted, it's important to note that they will be automatically converted to their standard counterparts '37' or '38' when saving the case object into the database.

#### Full RNA alignment view
A new key at the sample level is available, `rna_alignment_path`. Any RNA alignment cram/bam file added will be visible
on the RNA IGV views, together with any other previous RNA tracks, like splice junctions. The file index is expected at the same location.


### Other features

Scout version 4.72 contains additional new features. This is the complete list of changes introduced from the previous one:

## [4.72] CHANGELOG
### Added
- A GitHub action that checks for broken internal links in docs pages
- Link validation settings in mkdocs.yml file
- Load and display full RNA alignments on alignment viewer
- Genome build check when loading a case
- Extend event index to previous causative variants and always load them
### Fixed
- Documentation nav links for a few documents
- Slightly extended the BioNano Genomics Access integration docs
- Loading of SVs when VCF is missing the INFO.END field but has INFO.SVLEN field
- Escape protein sequence name (if available) in case general report to render special characters correctly
- CaseS HPO term searches for multiple terms works independent of order
- CaseS search regexp should not allow backslash
- CaseS cohort tags can contain whitespace and still match
- Remove diagnoses from cases even if OMIM term is not found in the database
- Parsing of disease-associated genes
### Changed
- Column width adjustment on caseS page
- Use Python 3.11 in tests
- Update some github actions
- Upgraded Pydantic to version 2
- Case validation fails on loading when associated files (alignments, VCFs and reports) are not present on disk
- Case validation fails on loading when custom images have format different then ["gif", "svg", "png", "jpg", "jpeg"]
- Custom images keys `case` and `str` in case config yaml file are renamed to `case_images` and `srt_variants_images`
- Simplify and speed up case general report code
- Speed up case retrieval in case_matching_causatives
- Upgrade pymongo to version 4
- When updating disease terms, check that all terms are consistent with a DiseaseTerm model before dropping the old collection
- Better separation between modules loading HPO terms and diseases
