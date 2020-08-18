## What's new in 4.20?

_Posted: August 18 2020_

This is a relatively small release justified by a fix to a **problem affecting only the delivery of results to our users at Clinical Genomics, SciLifeLab Stockholm**. Due to an update in our pipeline, cram alignments were not visible any more because the path to these files was replaced by the path to reduced mitochondrial alignments.

This is fixed in this release.

Scout version 4.20 contains additionally a number of new features. This is the complete list of changes introduced from the previous one:


## [4.20]
### Added
- Display number of filtered variants vs number of total variants in variants page
- Search case by HPO terms
- Dismiss variant column in the variant tables.
- Black and pre-commit packages to dev requirements

### Fixed
- Bug occurring when rerun is requested twice
- Peddy info fields in the demo config file
- Added load config safety check for multiple alignment files for one individual

### Changed
- Updated the documentation on how to create a new software release
- Genome build-aware cytobands coordinates
- Styling update of the Matchmaker card
- Select search type in case search form
