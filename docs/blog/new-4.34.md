## What's new in 4.34?

_Posted: May 17 2021_

This is a relatively large release, forced out by the need to fix a **problem affecting gene panels with outdated gene symbols starting in v4.21**.

### Gene panel HGNC symbol search bug
The 4.21 update allowed freer use of gene panels as lists, as well as the application of the latest version of the panel to each case.
HGNC symbols were previously handled by a separate mechanism, and subject to some validation checks.
Regrettably, HGNC symbols were taken as correct from the panels. This led to a situation where if the gene symbol had been updated in HGNC
but not on the latest panel version, variants in that gene could be missed on panel search. This is fixed in this release, and we now always use the HGNC id
behind the scenes for panel searches as well as manually entered HGNC symbol searches.

If you are on another instance than Solna, and want to check your database for panels, genes, cases and variants that could have been so compromised,
please find a new script in the scripts directory that you can modify to reflect your deploy date of 4.21.

### Other features
- Flask2 has been released very recently, and the codebase was updated to support the new version
- Saved filters can now be locked, preventing accidental deletion. This will be useful also for e.g. cancer and other pre-prescribed triage schemes.
- Saved filters can now be marked audited, leaving a line in the case event audit log, as well as on the general report. The analyst can so mark what
filters were applied and tried on the cases, communicating e.g. that both a stringent and less stringent quality filter has been tried,
  or say both AD_denovo, homozygous recessive and compound recessive variants were indeed checked.
- Several features have been added to cancer filters and the cancer variantS view has been refurbished and harmonized between Lund and Solna. Expect more similar
efforts in the next few releases!

Scout version 4.34 contains additionally a number of new features. This is the complete list of changes introduced from the previous one:

## [4.34] CHANGELOG
### Added
- Saved filter lock and unlock
- Filters can optionally be marked audited, logging the filter name, user and date on the case events and general report.
- Added `ClinVar hits` and `Cosmic hits` in cancer SNVs filters
- Added `ClinVar hits` to variants filter (rare disease track)
- Load cancer demo case in docker-compose files (default and demo file)
- Inclusive-language check using [woke](https://github.com/get-woke/woke) github action
- Add link to HmtVar for mitochondrial variants (if VCF is annotated with HmtNote)
- Grey background for dismissed compounds in variants list and variant page
- Pin badge for pinned compounds in variants list and variant page
- Support LoqusDB REST API queries
- Add a docker-compose-matchmaker under scout/containers/development to test matchmaker locally
- Script to investigate consequences of symbol search bug
### Fixed
- Make MitoMap link work for hg38 again
- Export Variants feature crashing when one of the variants has no primary transcripts
- Redirect to last visited variantS page when dismissing variants from variants list
- Improved matching of SVs Loqus occurrences in other cases
- Remove padding from the list inside (Matching causatives from other cases) panel
- Pass None to get_app function in CLI base since passing script_info to app factory functions was deprecated in Flask 2.0
- Fixed failing tests due to Flask update to version 2.0
- Speed up user events view
- Causative view sort out of memory error
- Use hgnc_id for gene filter query
- Typo in case controllers displaying an error every time a patient is matched against external MatchMaker nodes
- Do not crash while attemping an update for variant documents that are too big (> 16 MB)
- Old STR causatives may not have HGNC symbols - fix sort lambda
### Changed
- Remove parsing of case `genome_version`, since it's not used anywhere downstream
- Introduce deprecation warning for Loqus configs that are not dictionaries
- SV clinical filter no longer filters out sub 100 nt variants
- Count cases in LoqusDB by variant type
- Commit pulse repo badge temporarily set to weekly
- Sort ClinVar submissions objects by ascending "Last evaluated" date
- Refactored the MatchMaker integration as an extension
- Replaced some sensitive words as suggested by woke linter
- Documentation for load-configuration rewritten.
- Add styles to MatchMaker matches table

