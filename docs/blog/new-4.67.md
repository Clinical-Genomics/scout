## What's new in 4.67?

_Posted: April 6 2023_

This is a small release but adressing a recent **problem affecting the clinical filter** in particular of structural variants. Since VEP
introduced a few new SO terms for functional annotation, and we introduced them to Scout and MIP this autumn, sometimes new causative variants have
not been found with the clinical filter. Unfortunately the term `splice_polypyrimidine_tract_variant` has a slightly higher score than `coding_sequence_variant` - which is in clinical filter - in combination with filtering on `most_severe_consequence` rather than all transcript consequence can lead to
missing variants that should have been found. Recognising that `splice_polypyrimidine_tract_variant` is most often insignificant for an SNV but more important in an SV, we have introduced
an SV specific SO severity list, that contains this term, into the clinical filter.

### Other features

Scout version 4.67 contains additional new features. This is the complete list of changes introduced from the previous one:

## [4.67] CHANGELOG
### Added
- Prepare to filter local SV frequency
### Changed
- Clinical Filter for SVs includes `splice_polypyrimidine_tract_variant` as a severe consequence
- Clinical Filter for SVs includes local variant frequency freeze ("old") for filtering, starting at 30 counts
