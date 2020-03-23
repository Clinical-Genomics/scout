# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

About changelog [here](https://keepachangelog.com/en/1.0.0/)

## [x.x.x]

### Added
### Fixed
### Changed


## [4.14.1]

### Fixed
- Error when variant found in loqusdb is not loaded for other case

## [4.14]

### Added
- Use github actions to run tests
- Adds CLI command to update individual alignments path
- Update HPO terms using downloaded definitions files
- Option to use alternative flask config when running `scout serve`
- Requirement to use loqusdb >= 2.5 if integrated

### Fixed
- Do not display Pedigree panel in cancer view
- Do not rely on internet connection and services available when running CI tests
- Variant loading assumes GATK if no caller set given and GATK filter status is seen in FILTER
- Pass genome build param all the way in order to get the right gene mappings for cases with build 38
- Parse correctly variants with zero frequency values
- Continue even if there are problems to create a region vcf
- STR and cancer variant navigation back to variants pages could fail

### Changed
- Improved code that sends requests to the external APIs
- Updates ranges for user ranks to fit todays usage
- Run coveralls on github actions instead of travis
- Run pip checks on github actions instead of coveralls
- For hg38 cases, change gnomAD link to point to version 3.0 (which is hg38 based)
- Show pinned or causative STR variants a bit more human readable

## [4.13.1]

### Added
### Fixed
- Typo that caused not all clinvar conflicting interpretations to be loaded no matter what
- Parse and retrieve clinvar annotations from VEP-annotated (VEP 97+) CSQ VCF field
- Variant clinvar significance shown as `not provided` whenever is `Uncertain significance`
- Phenomizer query crashing when case has no HPO terms assigned
- Fixed a bug affecting `All SNVs and INDELs` page when variants don't have canonical transcript
- Add gene name or id in cancer variant view

### Changed
- Cancer Variant view changed "Variant:Transcript:Exon:HGVS" to "Gene:Transcript:Exon:HGVS"

## [4.13]

### Added
- ClinVar SNVs track in IGV
- Add SMA view with SMN Copy Number data
- Easier to assign OMIM diagnoses from case page
- OMIM terms and specific OMIM term page

### Fixed
- Bug when adding a new gene to a panel
- Restored missing recent delivery reports
- Fixed style and links to other reports in case side panel
- Deleting cases using display_name and institute not deleting its variants
- Fixed bug that caused coordinates filter to override other filters
- Fixed a problem with finding some INS in loqusdb
- Layout on SV page when local observations without cases are present
- Make scout compatible with the new HPO definition files from `http://compbio.charite.de/jenkins/`
- General report visualization error when SNVs display names are very long


### Changed


## [4.12.4]

### Fixed
- Layout on SV page when local observations without cases are present

## [4.12.3]

### Fixed
- Case report when causative or pinned SVs have non null allele frequencies

## [4.12.2]

### Fixed
- SV variant links now take you to the SV variant page again
- Cancer variant view has cleaner table data entries for "N/A" data
- Pinned variant case level display hotfix for cancer and str - more on this later
- Cancer variants show correct alt/ref reads mirroring alt frequency now
- Always load all clinical STR variants even if a region load is attempted - index may be missing
- Same case repetition in variant local observations

## [4.12.1]

### Fixed
- Bug in variant.gene when gene has no HGVS description


## [4.12]

### Added
- Accepts `alignment_path` in load config to pass bam/cram files
- Display all phenotypes on variant page
- Display hgvs coordinates on pinned and causatives
- Clear panel pending changes
- Adds option to setup the database with static files
- Adds cli command to download the resources from CLI that scout needs
- Adds dummy files for merged somatic SV and CNV; as well as merged SNV, and INDEL part of #1279
- Allows for upload of OMIM-AUTO gene panel from static files without api-key

### Fixed
- Cancer case HPO panel variants link
- Fix so that some drop downs have correct size
- First IGV button in str variants page
- Cancer case activates on SNV variants
- Cases activate when STR variants are viewed
- Always calculate code coverage
- Pinned/Classification/comments in all types of variants pages
- Null values for panel's custom_inheritance_models
- Discrepancy between the manual disease transcripts and those in database in gene-edit page
- ACMG classification not showing for some causatives
- Fix bug which caused IGV.js to use hg19 reference files for hg38 data
- Bug when multiple bam files sources with non-null values are available


### Changed
- Renamed `requests` file to `scout_requests`
- Cancer variant view shows two, instead of four, decimals for allele and normal


## [4.11.1]

### Fixed
- Institute settings page
- Link institute settings to sharing institutes choices

## [4.11.0]

### Added
- Display locus name on STR variant page
- Alternative key `GNOMADAF_popmax` for Gnomad popmax allele frequency
- Automatic suggestions on how to improve the code on Pull Requests
- Parse GERP, phastCons and phyloP annotations from vep annotated CSQ fields
- Avoid flickering comment popovers in variant list
- Parse REVEL score from vep annotated CSQ fields
- Allow users to modify general institute settings
- Optionally format code automatically on commit
- Adds command to backup vital parts `scout export database`
- Parsing and displaying cancer SV variants from Manta annotated VCF files
- Dismiss cancer snv variants with cancer-specific options
- Add IGV.js UPD, RHO and TIDDIT coverage wig tracks.


### Fixed
- Slightly darker page background
- Fixed an issued with parsed conservation values from CSQ
- Clinvar submissions accessible to all users of an institute
- Header toolbar when on Clinvar page now shows institute name correctly
- Case should not always inactivate upon update
- Show dismissed snv cancer variants as grey on the cancer variants page
- Improved style of mappability link and local observations on variant page
- Convert all the GET requests to the igv view to POST request
- Error when updating gene panels using a file containing BOM chars
- Add/replace gene radio button not working in gene panels


## [4.10.1]

### Fixed
- Fixed issue with opening research variants
- Problem with coveralls not called by Travis CI
- Handle Biomart service down in tests


## [4.10.0]

### Added
- Rank score model in causatives page
- Exportable HPO terms from phenotypes page
- AMP guideline tiers for cancer variants
- Adds scroll for the transcript tab
- Added CLI option to query cases on time since case event was added
- Shadow clinical assessments also on research variants display
- Support for CRAM alignment files
- Improved str variants view : sorting by locus, grouped by allele.
- Delivery report PDF export
- New mosaicism tag option
- Add or modify individuals' age or tissue type from case page
- Display GC and allele depth in causatives table.
- Included primary reference transcript in general report
- Included partial causative variants in general report
- Remove dependency of loqusdb by utilising the CLI

### Fixed
- Fixed update OMIM command bug due to change in the header of the genemap2 file
- Removed Mosaic Tag from Cancer variants
- Fixes issue with unaligned table headers that comes with hidden Datatables
- Layout in general report PDF export
- Fixed issue on the case statistics view. The validation bars didn't show up when all institutes were selected. Now they do.
- Fixed missing path import by importing pathlib.Path
- Handle index inconsistencies in the update index functions
- Fixed layout problems


## [4.9.0]

### Added
- Improved MatchMaker pages, including visible patient contacts email address
- New badges for the github repo
- Links to [GENEMANIA](genemania.org)
- Sort gene panel list on case view.
- More automatic tests
- Allow loading of custom annotations in VCF using the SCOUT_CUSTOM info tag.

### Fixed
- Fix error when a gene is added to an empty dynamic gene panel
- Fix crash when attempting to add genes on incorrect format to dynamic gene panel
- Manual rank variant tags could be saved in a "Select a tag"-state, a problem in the variants view.
- Same case evaluations are no longer shown as gray previous evaluations on the variants page
- Stay on research pages, even if reset, next first buttons are pressed..
- Overlapping variants will now be visible on variant page again
- Fix missing classification comments and links in evaluations page
- All prioritized cases are shown on cases page


## [4.8.3]

### Added

### Fixed
- Bug when ordering sanger
- Improved scrolling over long list of genes/transcripts


## [4.8.2]

### Added

### Fixed
- Avoid opening extra tab for coverage report
- Fixed a problem when rank model version was saved as floats and not strings
- Fixed a problem with displaying dismiss variant reasons on the general report
- Disable load and delete filter buttons if there are no saved filters
- Fix problem with missing verifications
- Remove duplicate users and merge their data and activity


## [4.8.1]

### Added

### Fixed
- Prevent login fail for users with id defined by ObjectId and not email
- Prevent the app from crashing with `AttributeError: 'NoneType' object has no attribute 'message'`


## [4.8.0]

### Added
- Updated Scout to use Bootstrap 4.3
- New looks for Scout
- Improved dashboard using Chart.js
- Ask before inactivating a case where last assigned user leaves it
- Genes can be manually added to the dynamic gene list directly on the case page
- Dynamic gene panels can optionally be used with clinical filter, instead of default gene panel
- Dynamic gene panels get link out to chanjo-report for coverage report
- Load all clinvar variants with clinvar Pathogenic, Likely Pathogenic and Conflicting pathogenic
- Show transcripts with exon numbers for structural variants
- Case sort order can now be toggled between ascending and descending.
- Variants can be marked as partial causative if phenotype is available for case.
- Show a frequency tooltip hover for SV-variants.
- Added support for LDAP login system
- Search snv and structural variants by chromosomal coordinates
- Structural variants can be marked as partial causative if phenotype is available for case.
- Show normal and pathologic limits for STRs in the STR variants view.
- Institute level persistent variant filter settings that can be retrieved and used.
- export causative variants to Excel
- Add support for ROH, WIG and chromosome PNGs in case-view

### Fixed
- Fixed missing import for variants with comments
- Instructions on how to build docs
- Keep sanger order + verification when updating/reloading variants
- Fixed and moved broken filter actions (HPO gene panel and reset filter)
- Fixed string conversion to number
- UCSC links for structural variants are now separated per breakpoint (and whole variant where applicable)
- Reintroduced missing coverage report
- Fixed a bug preventing loading samples using the command line
- Better inheritance models customization for genes in gene panels
- STR variant page back to list button now does its one job.
- Allows to setup scout without a omim api key
- Fixed error causing "favicon not found" flash messages
- Removed flask --version from base cli
- Request rerun no longer changes case status. Active or archived cases inactivate on upload.
- Fixed missing tooltip on the cancer variants page
- Fixed weird Rank cell in variants page
- Next and first buttons order swap
- Added pagination (and POST capability) to cancer variants.
- Improves loading speed for variant page
- Problem with updating variant rank when no variants
- Improved Clinvar submission form
- General report crashing when dismissed variant has no valid dismiss code
- Also show collaborative case variants on the All variants view.
- Improved phenotype search using dataTables.js on phenotypes page
- Search and delete users with `email` instead of `_id`
- Fixed css styles so that multiselect options will all fit one column


## [4.7.3]

### Added
- RankScore can be used with VCFs for vcf_cancer files

### Fixed
- Fix issue with STR view next page button not doing its one job.

### Deleted
- Removed pileup as a bam viewing option. This is replaced by IGV


## [4.7.2]

### Added
- Show earlier ACMG classification in the variant list

### Fixed
- Fixed igv search not working due to igv.js dist 2.2.17
- Fixed searches for cases with a gene with variants pinned or marked causative.
- Load variant pages faster after fixing other causatives query
- Fixed mitochondrial report bug for variants without genes

## [4.7.1]

### Added

### Fixed
- Fixed bug on genes page


## [4.7.0]

### Added
- Export genes and gene panels in build GRCh38
- Search for cases with variants pinned or marked causative in a given gene.
- Search for cases phenotypically similar to a case also from WUI.
- Case variant searches can be limited to similar cases, matching HPO-terms,
  phenogroups and cohorts.
- De-archive reruns and flag them as 'inactive' if archived
- Sort cases by analysis_date, track or status
- Display cases in the following order: prioritized, active, inactive, archived, solved
- Assign case to user when user activates it or asks for rerun
- Case becomes inactive when it has no assignees
- Fetch refseq version from entrez and use it in clinvar form
- Load and export of exons for all genes, independent on refseq
- Documentation for loading/updating exons
- Showing SV variant annotations: SV cgh frequencies, gnomad-SV, local SV frequencies
- Showing transcripts mapping score in segmental duplications
- Handle requests to Ensembl Rest API
- Handle requests to Ensembl Rest Biomart
- STR variants view now displays GT and IGV link.
- Description field for gene panels
- Export exons in build 37 and 38 using the command line

### Fixed
- Fixes of and induced by build tests
- Fixed bug affecting variant observations in other cases
- Fixed a bug that showed wrong gene coverage in general panel PDF export
- MT report only shows variants occurring in the specific individual of the excel sheet
- Disable SSL certifcate verification in requests to chanjo
- Updates how intervaltree and pymongo is used to void deprecated functions
- Increased size of IGV sample tracks
- Optimized tests


## [4.6.1]

### Added

### Fixed
- Missing 'father' and 'mother' keys when parsing single individual cases


## [4.6.0]

### Added
- Description of Scout branching model in CONTRIBUTING doc
- Causatives in alphabetical order, display ACMG classification and filter by gene.
- Added 'external' to the list of analysis type options
- Adds functionality to display "Tissue type". Passed via load config.
- Update to IGV 2.

### Fixed
- Fixed alignment visualization and vcf2cytosure availability for demo case samples
- Fixed 3 bugs affecting SV pages visualization
- Reintroduced the --version cli option
- Fixed variants query by panel (hpo panel + gene panel).
- Downloaded MT report contains excel files with individuals' display name
- Refactored code in parsing of config files.


## [4.5.1]

### Added

### Fixed
- update requirement to use PyYaml version >= 5.1
- Safer code when loading config params in cli base


## [4.5.0]

### Added
- Search for similar cases from scout view CLI
- Scout cli is now invoked from the app object and works under the app context

### Fixed
- PyYaml dependency fixed to use version >= 5.1


## [4.4.1]

### Added
- Display SV rank model version when available

### Fixed
- Fixed upload of delivery report via API


## [4.4.0]

### Added
- Displaying more info on the Causatives page and hiding those not causative at the case level
- Add a comment text field to Sanger order request form, allowing a message to be included in the email
- MatchMaker Exchange integration
- List cases with empty synopsis, missing HPO terms and phenotype groups.
- Search for cases with open research list, or a given case status (active, inactive, archived)

### Fixed
- Variant query builder split into several functions
- Fixed delivery report load bug


## [4.3.3]

### Added
- Different individual table for cancer cases

### Fixed
- Dashboard collects validated variants from verification events instead of using 'sanger' field
- Cases shared with collaborators are visible again in cases page
- Force users to select a real institute to share cases with (actionbar select fix)


## [4.3.2]

### Added
- Dashboard data can be filtered using filters available in cases page
- Causatives for each institute are displayed on a dedicated page
- SNVs and and SVs are searchable across cases by gene and rank score
- A more complete report with validated variants is downloadable from dashboard

### Fixed
- Clinsig filter is fixed so clinsig numerical values are returned
- Split multi clinsig string values in different elements of clinsig array
- Regex to search in multi clinsig string values or multi revstat string values
- It works to upload vcf files with no variants now
- Combined Pileup and IGV alignments for SVs having variant start and stop on the same chromosome


## [4.3.1]

### Added
- Show calls from all callers even if call is not available
- Instructions to install cairo and pango libs from WeasyPrint page
- Display cases with number of variants from CLI
- Only display cases with number of variants above certain treshold. (Also CLI)
- Export of verified variants by CLI or from the dashboard
- Extend case level queries with default panels, cohorts and phenotype groups.
- Slice dashboard statistics display using case level queries
- Add a view where all variants for an institute can be searched across cases, filtering on gene and rank score. Allows searching research variants for cases that have research open.

### Fixed
- Fixed code to extract variant conservation (gerp, phyloP, phastCons)
- Visualization of PDF-exported gene panels
- Reintroduced the exon/intron number in variant verification email
- Sex and affected status is correctly displayed on general report
- Force number validation in SV filter by size
- Display ensembl transcripts when no refseq exists


## [4.3.0]

### Added
- Mosaicism tag on variants
- Show and filter on SweGen frequency for SVs
- Show annotations for STR variants
- Show all transcripts in verification email
- Added mitochondrial export
- Adds alternative to search for SVs shorter that the given length
- Look for 'bcftools' in the `set` field of VCFs
- Display digenic inheritance from OMIM
- Displays what refseq transcript that is primary in hgnc

### Fixed

- Archived panels displays the correct date (not retroactive change)
- Fixed problem with waiting times in gene panel exports
- Clinvar fiter not working with human readable clinsig values

## [4.2.2]

### Fixed
- Fixed gene panel create/modify from CSV file utf-8 decoding error
- Updating genes in gene panels now supports edit comments and entry version
- Gene panel export timeout error

## [4.2.1]

### Fixed
- Re-introduced gene name(s) in verification email subject
- Better PDF rendering for excluded variants in report
- Problem to access old case when `is_default` did not exist on a panel


## [4.2.0]

### Added
- New index on variant_id for events
- Display overlapping compounds on variants view

### Fixed
- Fixed broken clinical filter


## [4.1.4]

### Added
- Download of filtered SVs

### Fixed
- Fixed broken download of filtered variants
- Fixed visualization issue in gene panel PDF export
- Fixed bug when updating gene names in variant controller


## [4.1.3]

### Fixed
- Displays all primary transcripts


## [4.1.2]

### Added
- Option add/replace when updating a panel via CSV file
- More flexible versioning of the gene panels
- Printing coverage report on the bottom of the pdf case report
- Variant verification option for SVs
- Logs uri without pwd when connecting
- Disease-causing transcripts in case report
- Thicker lines in case report
- Supports HPO search for cases, both terms or if described in synopsis
- Adds sanger information to dashboard

### Fixed
- Use db name instead of **auth** as default for authentication
- Fixes so that reports can be generated even with many variants
- Fixed sanger validation popup to show individual variants queried by user and institute.
- Fixed problem with setting up scout
- Fixes problem when exac file is not available through broad ftp
- Fetch transcripts for correct build in `adapter.hgnc_gene`

## [4.1.1]
- Fix problem with institute authentication flash message in utils
- Fix problem with comments
- Fix problem with ensembl link


## [4.1.0]

### Added
- OMIM phenotypes to case report
- Command to download all panel app gene panels `scout load panel --panel-app`
- Links to genenames.org and omim on gene page
- Popup on gene at variants page with gene information
- reset sanger status to "Not validated" for pinned variants
- highlight cases with variants to be evaluated by Sanger on the cases page
- option to point to local reference files to the genome viewer pileup.js. Documented in `docs.admin-guide.server`
- option to export single variants in `scout export variants`
- option to load a multiqc report together with a case(add line in load config)
- added a view for searching HPO terms. It is accessed from the top left corner menu
- Updates the variants view for cancer variants. Adds a small cancer specific filter for known variants
- Adds hgvs information on cancer variants page
- Adds option to update phenotype groups from CLI

### Fixed
- Improved Clinvar to submit variants from different cases. Fixed HPO terms in casedata according to feedback
- Fixed broken link to case page from Sanger modal in cases view
- Now only cases with non empty lists of causative variants are returned in `adapter.case(has_causatives=True)`
- Can handle Tumor only samples
- Long lists of HGNC symbols are now possible. This was previously difficult with manual, uploaded or by HPO search when changing filter settings due to GET request limitations. Relevant pages now use POST requests. Adds the dynamic HPO panel as a selection on the gene panel dropdown.
- Variant filter defaults to default panels also on SV and Cancer variants pages.

## [4.0.0]

### WARNING ###

This is a major version update and will require that the backend of pre releases is updated.
Run commands:

```
$scout update genes
$scout update hpo
```

- Created a Clinvar submission tool, to speed up Clinvar submission of SNVs and SVs
- Added an analysis report page (html and PDF format) containing phenotype, gene panels and variants that are relevant to solve a case.

### Fixed
- Optimized evaluated variants to speed up creation of case report
- Moved igv and pileup viewer under a common folder
- Fixed MT alignment view pileup.js
- Fixed coordinates for SVs with start chromosome different from end chromosome
- Global comments shown across cases and institutes. Case-specific variant comments are shown only for that specific case.
- Links to clinvar submitted variants at the cases level
- Adapts clinvar parsing to new format
- Fixed problem in `scout update user` when the user object had no roles
- Makes pileup.js use online genome resources when viewing alignments. Now any instance of Scout can make use of this functionality.
- Fix ensembl link for structural variants
- Works even when cases does not have `'madeline_info'`
- Parses Polyphen in correct way again
- Fix problem with parsing gnomad from VEP

### Added
- Added a PDF export function for gene panels
- Added a "Filter and export" button to export custom-filtered SNVs to CSV file
- Dismiss SVs
- Added IGV alignments viewer
- Read delivery report path from case config or CLI command
- Filter for spidex scores
- All HPO terms are now added and fetched from the correct source (https://github.com/obophenotype/human-phenotype-ontology/blob/master/hp.obo)
- New command `scout update hpo`
- New command `scout update genes` will fetch all the latest information about genes and update them
- Load **all** variants found on chromosome **MT**
- Adds choice in cases overview do show as many cases as user like

### Removed
- pileup.min.js and pileup css are imported from a remote web location now
- All source files for HPO information, this is instead fetched directly from source
- All source files for gene information, this is instead fetched directly from source

## [3.0.0]
### Fixed
- hide pedigree panel unless it exists

## [1.5.1] - 2016-07-27
### Fixed
- look for both ".bam.bai" and ".bai" extensions

## [1.4.0] - 2016-03-22
### Added
- support for local frequency through loqusdb
- bunch of other stuff

## [1.3.0] - 2016-02-19
### Fixed
- Update query-phenomizer and add username/password

### Changed
- Update the way a case is checked for rerun-status

### Added
- Add new button to mark a case as "checked"
- Link to clinical variants _without_ 1000G annotation

## [1.2.2] - 2016-02-18
### Fixed
- avoid filtering out variants lacking ExAC and 1000G annotations

## [1.1.3] - 2015-10-01
### Fixed
- persist (clinical) filter when clicking load more
- fix #154 by robustly setting clinical filter func. terms

## [1.1.2] - 2015-09-07
### Fixed
- avoid replacing coverage report with none
- update SO terms, refactored

## [1.1.1] - 2015-08-20
### Fixed
- fetch case based on collaborator status (not owner)

## [1.1.0] - 2015-05-29
### Added
- link(s) to SNPedia based on RS-numbers
- new Jinja filter to "humanize" decimal numbers
- show gene panels in variant view
- new Jinja filter for decoding URL encoding
- add indicator to variants in list that have comments
- add variant number threshold and rank score threshold to load function
- add event methods to mongo adapter
- add tests for models
- show badge "old" if comment was written for a previous analysis

### Changed
- show cDNA change in transcript summary unless variant is exonic
- moved compounds table further up the page
- show dates for case uploads in ISO format
- moved variant comments higher up on page
- updated documentation for pages
- read in coverage report as blob in database and serve directly
- change ``OmimPhenotype`` to ``PhenotypeTerm``
- reorganize models sub-package
- move events (and comments) to separate collection
- only display prev/next links for the research list
- include variant type in breadcrumbs e.g. "Clinical variants"

### Removed
- drop dependency on moment.js

### Fixed
- show the same level of detail for all frequencies on all pages
- properly decode URL encoded symbols in amino acid/cDNA change strings
- fixed issue with wipe permissions in MongoDB
- include default gene lists in "variants" link in breadcrumbs

## [1.0.2] - 2015-05-20
### Changed
- update case fetching function

### Fixed
- handle multiple cases with same id

## [1.0.1] - 2015-04-28
### Fixed
- Fix building URL parameters in cases list Vue component

## [1.0.0] - 2015-04-12
Codename: Sara Lund

![Release 1.0](artwork/releases/release-1-0.jpg)

### Added
- Add email logging for unexpected errors
- New command line tool for deleting case

### Changed
- Much improved logging overall
- Updated documentation/usage guide
- Removed non-working IGV link

### Fixed
- Show sample display name in GT call
- Various small bug fixes
- Make it easier to hover over popups

## [0.0.2-rc1] - 2015-03-04
### Added
- add protein table for each variant
- add many more external links
- add coverage reports as PDFs

### Changed
- incorporate user feedback updates
- big refactor of load scripts

## [0.0.2-rc2] - 2015-03-04
### Changes
- add gene table with gene description
- reorganize inheritance models box

### Fixed
- avoid overwriting gene list on "research" load
- fix various bugs in external links

## [0.0.2-rc3] - 2015-03-05
### Added
- Activity log feed to variant view
- Adds protein change strings to ODM and Sanger email

### Changed
- Extract activity log component to macro

### Fixes
- Make Ensembl transcript links use archive website
