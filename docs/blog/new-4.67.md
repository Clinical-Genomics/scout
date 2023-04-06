## What's new in 4.67?

_Posted: April 6 2023_

This is a small release but adressing a recent **problem affecting the clinical filter** in particular of structural variants. Since VEP
introduced a few new SO terms for functional annotation, and we introduced them to Scout and MIP this autumn, sometimes new causative variants have
not been found with the clinical filter. Unfortunately the term `splice_polypyrimidine_tract_variant` has a slightly higher score than `coding_sequence_variant` - which is in clinical filter - in combination with filtering on `most_severe_consequence` rather than all transcript consequence can lead to
missing variants that should have been found. Recognising that `splice_polypyrimidine_tract_variant` is most often insignificant for an SNV but more important in an SV, we have introduced
an SV specific SO severity list, that contains this term, into the clinical filter.

### Other features
- Flask2 has been released very recently, and the codebase was updated to support the new version
- Saved filters can now be locked, preventing accidental deletion. This will be useful also for e.g. cancer and other pre-prescribed triage schemes.
- Saved filters can now be marked audited, leaving a line in the case event audit log, as well as on the general report. The analyst can so mark what
filters were applied and tried on the cases, communicating e.g. that both a stringent and less stringent quality filter has been tried,
  or say both AD_denovo, homozygous recessive and compound recessive variants were indeed checked.
- Several features have been added to cancer filters and the cancer variantS view has been refurbished and harmonized between Lund and Solna. Expect more similar
efforts in the next few releases!

Scout version 4.67 contains additional new features. This is the complete list of changes introduced from the previous one:

## [4.67] CHANGELOG

