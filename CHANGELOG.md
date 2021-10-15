# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

About changelog [here](https://keepachangelog.com/en/1.0.0/)

## []
### Added
### Fixed
### Changed

## [4.40]
### Added
- A .cff citation file
- Phenotype search API endpoint
- Added pagination to phenotype API
- Extend case search to include internal MongoDB id
- Support for connecting to a MongoDB replica set (.py config files)
- Support for connecting to a MongoDB replica set (.yaml config files)
### Fixed
- Command to load the OMIM gene panel (`scout load panel --omim`)
- Unify style of pinned and causative variants' badges on case page
- Removed automatic spaces after punctuation in comments
- Remove the hardcoded number of total individuals from the variant's old observations panel
- Send delete requests to a connected Beacon using the DELETE method
- Layout of the SNV and SV variant page - move frequency up
### Changed
- Stop updating database indexes after loading exons via command line
- Display validation status badge also for not Sanger-sequenced variants
- Moved Frequencies, Severity and Local observations panels up in RD variants page
- Enabled Flask CORS to communicate CORS status to js apps
- Moved the code preparing the transcripts overview to the backend
- Refactored and filtered json data used in general case report
- Changed the database used in docker-compose file to use the official MongoDB v4.4 image
- Modified the Python (3.6, 3.8) and MongoDB (3.2, 4.4, 5.0) versions used in testing matrices (GitHub actions)
- Capitalize case search terms on institute and dashboard pages

## [4.39]
### Added
- COSMIC IDs collected from CSQ field named `COSMIC`
### Fixed
- Link to other causative variants on variant page
- Allow multiple COSMIC links for a cancer variant
- Fix floating text in severity box #2808
- Fixed MitoMap and HmtVar links for hg38 cases
- Do not open new browser tabs when downloading files
- Selectable IGV tracks on variant page
- Missing splice junctions button on variant page
- Refactor variantS representative gene selection, and use it also for cancer variant summary
### Changed
- Improve Javascript performance for displaying Chromograph images
- Make ClinVar classification more evident in cancer variant page

## [4.38]
### Added
- Option to hide Alamut button in the app config file
### Fixed
- Library deprecation warning fixed (insert is deprecated. Use insert_one or insert_many instead)
- Update genes command will not trigger an update of database indices any more
- Missing resources in temporary downloading directory when updating genes using the command line
- Restore previous variant ACMG classification in a scrollable div
- Loading spinner not stopping after downloading PDF case reports and variant list export
- Add extra Alamut links higher up on variant pages
- Improve UX for phenotypes in case page
- Filter and export of STR variants
- Update look of variants page navigation buttons
### Changed

## [4.37]
### Added
- Highlight and show version number for RefSeq MANE transcripts.
- Added integration to a rerunner service for toggling reanalysis with updated pedigree information
- SpliceAI display and parsing from VEP CSQ
- Display matching tiered variants for cancer variants
- Display a loading icon (spinner) until the page loads completely
- Display filter badges in cancer variants list
- Update genes from pre-downloaded file resources
- On login, OS, browser version and screen size are saved anonymously to understand how users are using Scout
- API returning institutes data for a given user: `/api/v1/institutes`
- API returning case data for a given institute: `/api/v1/institutes/<institute_id>/cases`
- Added GMS and Lund university hospital logos to login page
- Made display of Swedac logo configurable
- Support for displaying custom images in case view
- Individual-specific HPO terms
- Optional alamut_key in institute settings for Alamut Plus software
- Case report API endpoint
- Tooltip in case explaining that genes with genome build different than case genome build will not be added to dynamic HPO panel.
- Add DeepVariant as a caller
### Fixed
- Updated IGV to v2.8.5 to solve missing gene labels on some zoom levels
- Demo cancer case config file to load somatic SNVs and SVs only.
- Expand list of refseq trancripts in ClinVar submission form
- Renamed `All SNVs and INDELs` institute sidebar element to `Search SNVs and INDELs` and fixed its style.
- Add missing parameters to case load-config documentation
- Allow creating/editing gene panels and dynamic gene panels with genes present in genome build 38
- Bugfix broken Pytests
- Bulk dismissing variants error due to key conversion from string to integer
- Fix typo in index documentation
- Fixed crash in institute settings page if "collaborators" key is not set in database
- Don't stop Scout execution if LoqusDB call fails and print stacktrace to log
- Bug when case contains custom images with value `None`
- Bug introduced when fixing another bug in Scout-LoqusDB interaction
- Loading of OMIM diagnoses in Scout demo instance
- Remove the docker-compose with chanjo integration because it doesn't work yet.
- Fixed standard docker-compose with scout demo data and database
- Clinical variant assessments not present for pinned and causative variants on case page.
- MatchMaker matching one node at the time only
- Remove link from previously tiered variants badge in cancer variants page
- Typo in gene cell on cancer variants page
- Managed variants filter form
### Changed
- Better naming for variants buttons on cancer track (somatic, germline). Also show cancer research button if available.
- Load case with missing panels in config files, but show warning.
- Changing the (Female, Male) symbols to (F/M) letters in individuals_table and case-sma.
- Print stacktrace if case load command fails
- Added sort icon and a pointer to the cursor to all tables with sortable fields
- Moved variant, gene and panel info from the basic pane to summary panel for all variants.
- Renamed `Basics` panel to `Classify` on variant page.
- Revamped `Basics` panel to a panel dedicated to classify variants
- Revamped the summary panel to be more compact.
- Added dedicated template for cancer variants
- Removed Gene models, Gene annotations and Conservation panels for cancer variants
- Reorganized the orders of panels for variant and cancer variant views
- Added dedicated variant quality panel and removed relevant panes
- A more compact case page
- Removed OMIM genes panel
- Make genes panel, pinned variants panel, causative variants panel and ClinVar panel scrollable on case page
- Update to Scilifelab's 2020 logo
- Update Gens URL to support Gens v2.0 format
- Refactor tests for parsing case configurations
- Updated links to HPO downloadable resources
- Managed variants filtering defaults to all variant categories
- Changing the (Kind) drop-down according to (Category) drop-down in Managed variant add variant
- Moved Gens button to individuals table
- Check resource files availability before starting updating OMIM diagnoses
- Fix typo in `SHOW_OBSERVED_VARIANT_ARCHIVE` config param

## [4.36]
### Added
- Parse and save splice junction tracks from case config file
- Tooltip in observations panel, explaining that case variants with no link might be old variants, not uploaded after a case rerun
### Fixed
- Warning on overwriting variants with same position was no longer shown
- Increase the height of the dropdowns to 425px
- More indices for the case table as it grows, specifically for causatives queries
- Splice junction tracks not centered over variant genes
- Total number of research variants count
- Update variants stats in case documents every time new variants are loaded
- Bug in flashing warning messages when filtering variants
### Changed
- Clearer warning messages for genes and gene/gene-panels searches in variants filters

## [4.35]
### Added
- A new index for hgnc_symbol in the hgnc_gene collection
- A Pedigree panel in STR page
- Display Tier I and II variants in case view causatives card for cancer cases
### Fixed
- Send partial file data to igv.js when visualizing sashimi plots with splice junction tracks
- Research variants filtering by gene
- Do not attempt to populate annotations for not loaded pinned/causatives
- Add max-height to all dropdowns in filters
### Changed
- Switch off non-clinical gene warnings when filtering research variants
- Don't display OMIM disease card in case view for cancer cases
- Refactored Individuals and Causative card in case view for cancer cases
- Update and style STR case report

## [4.34]
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
- Added GATK to list of SV and cancer SV callers
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
- Do not crash while attempting an update for variant documents that are too big (> 16 MB)
- Old STR causatives (and other variants) may not have HGNC symbols - fix sort lambda
- Check if gene_obj has primary_transcript before trying to access it
- Warn if a gene manually searched is in a clinical panel with an outdated name when filtering variants
- ChrPos split js not needed on STR page yet
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
- More detailed info on the data shared in MatchMaker submission form

## [4.33.1]
### Fixed
- Include markdown for release autodeploy docs
- Use standard inheritance model in ClinVar (https://ftp.ncbi.nlm.nih.gov/pub/GTR/standard_terms/Mode_of_inheritance.txt)
- Fix issue crash with variants that have been unflagged causative not being available in other causatives
### Added
### Changed

## [4.33]
### Fixed
- Command line crashing when updating an individual not found in database
- Dashboard page crashing when filters return no data
- Cancer variants filter by chromosome
- /api/v1/genes now searches for genes in all genome builds by default
- Upgraded igv.js to version 2.8.1 (Fixed Unparsable bed record error)
### Added
- Autodeploy docs on release
- Documentation for updating case individuals tracks
- Filter cases and dashboard stats by analysis track
### Changed
- Changed from deprecated db update method
- Pre-selected fields to run queries with in dashboard page
- Do not filter by any institute when first accessing the dashboard
- Removed OMIM panel in case view for cancer cases
- Display Tier I and II variants in case view causatives panel for cancer cases
- Refactored Individuals and Causative panels in case view for cancer cases

## [4.32.1]
### Fixed
- iSort lint check only
### Changed
- Institute cases page crashing when a case has track:Null
### Added

## [4.32]
### Added
- Load and show MITOMAP associated diseases from VCF (INFO field: MitomapAssociatedDiseases, via HmtNote)
- Show variant allele frequencies for mitochondrial variants (GRCh38 cases)
- Extend "public" json API with diseases (OMIM) and phenotypes (HPO)
- HPO gene list download now has option for clinical and non-clinical genes
- Display gene splice junctions data in sashimi plots
- Update case individuals with splice junctions tracks
- Simple Docker compose for development with local build
- Make Phenomodels subpanels collapsible
- User side documentation of cytogenomics features (Gens, Chromograph, vcf2cytosure, rhocall)
- iSort GitHub Action
- Support LoqusDB REST API queries
### Fixed
- Show other causative once, even if several events point to it
- Filtering variants by mitochondrial chromosome for cases with genome build=38
- HPO gene search button triggers any warnings for clinical / non-existing genes also on first search
- Fixed a bug in variants pages caused by MT variants without alt_frequency
- Tests for CADD score parsing function
- Fixed the look of IGV settings on SNV variant page
- Cases analyzed once shown as `rerun`
- Missing case track on case re-upload
- Fixed severity rank for SO term "regulatory region ablation"
### Changed
- Refactor according to CodeFactor - mostly reuse of duplicated code
- Phenomodels language adjustment
- Open variants in a new window (from variants page)
- Open overlapping and compound variants in a new window (from variant page)
- gnomAD link points to gnomAD v.3 (build GRCh38) for mitochondrial variants.
- Display only number of affected genes for dismissed SVs in general report
- Chromosome build check when populating the variants filter chromosome selection
- Display mitochondrial and rare diseases coverage report in cases with missing 'rare' track

## [4.31.1]
### Added
### Changed
- Remove mitochondrial and coverage report from cancer cases sidebar
### Fixed
- ClinVar page when dbSNP id is None

## [4.31]
### Added
- gnomAD annotation field in admin guide
- Export also dynamic panel genes not associated to an HPO term when downloading the HPO panel
- Primary HGNC transcript info in variant export files
- Show variant quality (QUAL field from vcf) in the variant summary
- Load/update PDF gene fusion reports (clinical and research) generated with Arriba
- Support new MANE annotations from VEP (both MANE Select and MANE Plus Clinical)
- Display on case activity the event of a user resetting all dismissed variants
- Support gnomAD population frequencies for mitochondrial variants
- Anchor links in Casedata ClinVar panels to redirect after renaming individuals
### Fixed
- Replace old docs link www.clinicalgenomics.se/scout with new https://clinical-genomics.github.io/scout
- Page formatting issues whenever case and variant comments contain extremely long strings with no spaces
- Chromograph images can be one column and have scrollbar. Removed legacy code.
- Column labels for ClinVar case submission
- Page crashing looking for LoqusDB observation when variant doesn't exist
- Missing inheritance models and custom inheritance models on newly created gene panels
- Accept only numbers in managed variants filter as position and end coordinates
- SNP id format and links in Variant page, ClinVar submission form and general report
- Case groups tooltip triggered only when mouse is on the panel header
### Changed
- A more compact case groups panel
- Added landscape orientation CSS style to cancer coverage and QC demo report
- Improve user documentation to create and save new gene panels
- Removed option to use space as separator when uploading gene panels
- Separating the columns of standard and custom inheritance models in gene panels
- Improved ClinVar instructions for users using non-English Excel

## [4.30.2]
### Added
### Fixed
- Use VEP RefSeq ID if RefSeq list is empty in RefSeq transcripts overview
- Bug creating variant links for variants with no end_chrom
### Changed

## [4.30.1]
### Added
### Fixed
- Cryptography dependency fixed to use version < 3.4
### Changed

## [4.30]
### Added
- Introduced a `reset dismiss variant` verb
- Button to reset all dismissed variants for a case
- Add black border to Chromograph ideograms
- Show ClinVar annotations on variantS page
- Added integration with GENS, copy number visualization tool
- Added a VUS label to the manual classification variant tags
- Add additional information to SNV verification emails
- Tooltips documenting manual annotations from default panels
- Case groups now show bam files from all cases on align view
### Fixed
- Center initial igv view on variant start with SNV/indels
- Don't set initial igv view to negative coordinates
- Display of GQ for SV and STR
- Parsing of AD and related info for STRs
- LoqusDB field in institute settings accepts only existing Loqus instances
- Fix DECIPHER link to work after DECIPHER migrated to GRCh38
- Removed visibility window param from igv.js genes track
- Updated HPO download URL
- Patch HPO download test correctly
- Reference size on STR hover not needed (also wrong)
- Introduced genome build check (allowed values: 37, 38, "37", "38") on case load
- Improve case searching by assignee full name
- Populating the LoqusDB select in institute settings
### Changed
- Cancer variants table header (pop freq etc)
- Only admin users can modify LoqusDB instance in Institute settings
- Style of case synopsis, variants and case comments
- Switched to igv.js 2.7.5
- Do not choke if case is missing research variants when research requested
- Count cases in LoqusDB by variant type
- Introduce deprecation warning for Loqus configs that are not dictionaries
- Improve create new gene panel form validation
- Make XM- transcripts less visible if they don't overlap with transcript refseq_id in variant page
- Color of gene panels and comments panels on cases and variant pages
- Do not choke if case is missing research variants when reserch requested

## [4.29.1]
### Added
### Fixed
- Always load STR variants regardless of RankScore threshold (hotfix)
### Changed

## [4.29]
### Added
- Added a page about migrating potentially breaking changes to the documentation
- markdown_include in development requirements file
- STR variants filter
- Display source, Z-score, inheritance pattern for STR annotations from Stranger (>0.6.1) if available
- Coverage and quality report to cancer view
### Fixed
- ACMG classification page crashing when trying to visualize a classification that was removed
- Pretty print HGVS on gene variants (URL-decode VEP)
- Broken or missing link in the documentation
- Multiple gene names in ClinVar submission form
- Inheritance model select field in ClinVar submission
- IGV.js >2.7.0 has an issue with the gene track zoom levels - temp freeze at 2.7.0
- Revert CORS-anywhere and introduce a local http proxy for cloud tracks
### Changed

## [4.28]
### Added
- Chromograph integration for displaying PNGs in case-page
- Add VAF to cancer case general report, and remove some of its unused fields
- Variants filter compatible with genome browser location strings
- Support for custom public igv tracks stored on the cloud
- Add tests to increase testing coverage
- Update case variants count after deleting variants
- Update IGV.js to latest (v2.7.4)
- Bypass igv.js CORS check using `https://github.com/Rob--W/cors-anywhere`
- Documentation on default and custom IGV.js tracks (admin docs)
- Lock phenomodels so they're editable by admins only
- Small case group assessment sharing
- Tutorial and files for deploying app on containers (Kubernetes pods)
- Canonical transcript and protein change of canonical transcript in exported variants excel sheet
- Support for Font Awesome version 6
- Submit to Beacon from case page sidebar
- Hide dismissed variants in variants pages and variants export function
- Systemd service files and instruction to deploy Scout using podman
### Fixed
- Bugfix: unused `chromgraph_prefix |tojson` removed
- Freeze coloredlogs temporarily
- Marrvel link
- Don't show TP53 link for silent or synonymous changes
- OMIM gene field accepts any custom number as OMIM gene
- Fix Pytest single quote vs double quote string
- Bug in gene variants search by similar cases and no similar case is found
- Delete unused file `userpanel.py`
- Primary transcripts in variant overview and general report
- Google OAuth2 login setup in README file
- Redirect to 'missing file'-icon if configured Chromograph file is missing
- Javascript error in case page
- Fix compound matching during variant loading for hg38
- Cancer variants view containing variants dismissed with cancer-specific reasons
- Zoom to SV variant length was missing IGV contig select
- Tooltips on case page when case has no default gene panels
### Changed
- Save case variants count in case document and not in sessions
- Style of gene panels multiselect on case page
- Collapse/expand main HPO checkboxes in phenomodel preview
- Replaced GQ (Genotype quality) with VAF (Variant allele frequency) in cancer variants GT table
- Allow loading of cancer cases with no tumor_purity field
- Truncate cDNA and protein changes in case report if longer than 20 characters


## [4.27]
### Added
- Exclude one or more variant categories when running variants delete command
### Fixed
### Changed

## [4.26.1]
### Added
### Fixed
- Links with 1-letter aa codes crash on frameshift etc
### Changed

## [4.26]
### Added
- Extend the delete variants command to print analysis date, track, institute, status and research status
- Delete variants by type of analysis (wgs|wes|panel)
- Links to cBioPortal, MutanTP53, IARC TP53, OncoKB, MyCancerGenome, CIViC
### Fixed
- Deleted variants count
### Changed
- Print output of variants delete command as a tab separated table

## [4.25]
### Added
- Command line function to remove variants from one or all cases
### Fixed
- Parse SMN None calls to None rather than False

## [4.24.1]
### Fixed
- Install requirements.txt via setup file

## [4.24]
### Added
- Institute-level phenotype models with sub-panels containing HPO and OMIM terms
- Runnable Docker demo
- Docker image build and push github action
- Makefile with shortcuts to docker commands
- Parse and save synopsis, phenotype and cohort terms from config files upon case upload
### Fixed
- Update dismissed variant status when variant dismissed key is missing
- Breakpoint two IGV button now shows correct chromosome when different from bp1
- Missing font lib in Docker image causing the PDF report download page to crash
- Sentieon Manta calls lack Somaticscore - load anyway
- ClinVar submissions crashing due to pinned variants that are not loaded
- Point ExAC pLI score to new gnomad server address
- Bug uploading cases missing phenotype terms in config file
- STRs loaded but not shown on browser page
- Bug when using adapter.variant.get_causatives with case_id without causatives
- Problem with fetching "solved" from scout export cases cli
- Better serialising of datetime and bson.ObjectId
- Added `volumes` folder to .gitignore
### Changed
- Make matching causative and managed variants foldable on case page
- Remove calls to PyMongo functions marked as deprecated in backend and frontend(as of version 3.7).
- Improved `scout update individual` command
- Export dynamic phenotypes with ordered gene lists as PDF


## [4.23]
### Added
- Save custom IGV track settings
- Show a flash message with clear info about non-valid genes when gene panel creation fails
- CNV report link in cancer case side navigation
- Return to comment section after editing, deleting or submitting a comment
- Managed variants
- MT vs 14 chromosome mean coverage stats if Scout is connected to Chanjo
### Fixed
- missing `vcf_cancer_sv` and `vcf_cancer_sv_research` to manual.
- Split ClinVar multiple clnsig values (slash-separated) and strip them of underscore for annotations without accession number
- Timeout of `All SNVs and INDELs` page when no valid gene is provided in the search
- Round CADD (MIPv9)
- Missing default panel value
- Invisible other causatives lines when other causatives lack gene symbols
### Changed
- Do not freeze mkdocs-material to version 4.6.1
- Remove pre-commit dependency

## [4.22]
### Added
- Editable cases comments
- Editable variants comments
### Fixed
- Empty variant activity panel
- STRs variants popover
- Split new ClinVar multiple significance terms for a variant
- Edit the selected comment, not the latest
### Changed
- Updated RELEASE docs.
- Pinned variants card style on the case page
- Merged `scout export exons` and `scout view exons` commands


## [4.21.2]
### Added
### Fixed
- Do not pre-filter research variants by (case-default) gene panels
- Show OMIM disease tooltip reliably
### Changed

## [4.21.1]
### Added
### Fixed
- Small change to Pop Freq column in variants ang gene panels to avoid strange text shrinking on small screens
- Direct use of HPO list for Clinical HPO SNV (and cancer SNV) filtering
- PDF coverage report redirecting to login page
### Changed
- Remove the option to dismiss single variants from all variants pages
- Bulk dismiss SNVs, SVs and cancer SNVs from variants pages

## [4.21]
### Added
- Support to configure LoqusDB per institute
- Highlight causative variants in the variants list
- Add tests. Mostly regarding building internal datatypes.
- Remove leading and trailing whitespaces from panel_name and display_name when panel is created
- Mark MANE transcript in list of transcripts in "Transcript overview" on variant page
- Show default panel name in case sidebar
- Previous buttons for variants pagination
- Adds a gh action that checks that the changelog is updated
- Adds a gh action that deploys new releases automatically to pypi
- Warn users if case default panels are outdated
- Define institute-specific gene panels for filtering in institute settings
- Use institute-specific gene panels in variants filtering
- Show somatic VAF for pinned and causative variants on case page

### Fixed
- Report pages redirect to login instead of crashing when session expires
- Variants filter loading in cancer variants page
- User, Causative and Cases tables not scaling to full page
- Improved docs for an initial production setup
- Compatibility with latest version of Black
- Fixed tests for Click>7
- Clinical filter required an extra click to Filter to return variants
- Restore pagination and shrink badges in the variants page tables
- Removing a user from the command line now inactivates the case only if user is last assignee and case is active
- Bugfix, LoqusDB per institute feature crashed when institute id was empty string
- Bugfix, LoqusDB calls where missing case count
- filter removal and upload for filters deleted from another page/other user
- Visualize outdated gene panels info in a popover instead of a tooltip in case page side panel

### Changed
- Highlight color on normal STRs in the variants table from green to blue
- Display breakpoints coordinates in verification emails only for structural variants


## [4.20]
### Added
- Display number of filtered variants vs number of total variants in variants page
- Search case by HPO terms
- Dismiss variant column in the variants tables
- Black and pre-commit packages to dev requirements

### Fixed
- Bug occurring when rerun is requested twice
- Peddy info fields in the demo config file
- Added load config safety check for multiple alignment files for one individual
- Formatting of cancer variants table
- Missing Score in SV variants table

### Changed
- Updated the documentation on how to create a new software release
- Genome build-aware cytobands coordinates
- Styling update of the Matchmaker card
- Select search type in case search form


## [4.19]

### Added
- Show internal ID for case
- Add internal ID for downloaded CGH files
- Export dynamic HPO gene list from case page
- Remove users as case assignees when their account is deleted
- Keep variants filters panel expanded when filters have been used

### Fixed
- Handle the ProxyFix ModuleNotFoundError when Werkzeug installed version is >1.0
- General report formatting issues whenever case and variant comments contain extremely long strings with no spaces

### Changed
- Created an institute wrapper page that contains list of cases, causatives, SNVs & Indels, user list, shared data and institute settings
- Display case name instead of case ID on clinVar submissions
- Changed icon of sample update in clinVar submissions


## [4.18]

### Added
- Filter cancer variants on cytoband coordinates
- Show dismiss reasons in a badge with hover for clinical variants
- Show an ellipsis if 10 cases or more to display with loqusdb matches
- A new blog post for version 4.17
- Tooltip to better describe Tumor and Normal columns in cancer variants
- Filter cancer SNVs and SVs by chromosome coordinates
- Default export of `Assertion method citation` to clinVar variants submission file
- Button to export up to 500 cancer variants, filtered or not
- Rename samples of a clinVar submission file

### Fixed
- Apply default gene panel on return to cancer variantS from variant view
- Revert to certificate checking when asking for Chanjo reports
- `scout download everything` command failing while downloading HPO terms

### Changed
- Turn tumor and normal allelic fraction to decimal numbers in tumor variants page
- Moved clinVar submissions code to the institutes blueprints
- Changed name of clinVar export files to FILENAME.Variant.csv and FILENAME.CaseData.csv
- Switched Google login libraries from Flask-OAuthlib to Authlib


## [4.17.1]

### Fixed
- Load cytobands for cases with chromosome build not "37" or "38"


## [4.17]

### Added
- COSMIC badge shown in cancer variants
- Default gene-panel in non-cancer structural view in url
- Filter SNVs and SVs by cytoband coordinates
- Filter cancer SNV variants by alt allele frequency in tumor
- Correct genome build in UCSC link from structural variant page



### Fixed
- Bug in clinVar form when variant has no gene
- Bug when sharing cases with the same institute twice
- Page crashing when removing causative variant tag
- Do not default to GATK caller when no caller info is provided for cancer SNVs


## [4.16.1]

### Fixed
- Fix the fix for handling of delivery reports for rerun cases

## [4.16]

### Added
- Adds possibility to add "lims_id" to cases. Currently only stored in database, not shown anywhere
- Adds verification comment box to SVs (previously only available for small variants)
- Scrollable pedigree panel

### Fixed
- Error caused by changes in WTForm (new release 2.3.x)
- Bug in OMIM case page form, causing the page to crash when a string was provided instead of a numerical OMIM id
- Fix Alamut link to work properly on hg38
- Better handling of delivery reports for rerun cases
- Small CodeFactor style issues: matchmaker results counting, a couple of incomplete tests and safer external xml
- Fix an issue with Phenomizer introduced by CodeFactor style changes

### Changed
- Updated the version of igv.js to 2.5.4

## [4.15.1]

### Added
- Display gene names in ClinVar submissions page
- Links to Varsome in variant transcripts table

### Fixed
- Small fixes to ClinVar submission form
- Gene panel page crash when old panel has no maintainers

## [4.15]

### Added
- Clinvar CNVs IGV track
- Gene panels can have maintainers
- Keep variant actions (dismissed, manual rank, mosaic, acmg, comments) upon variant re-upload
- Keep variant actions also on full case re-upload

### Fixed
- Fix the link to Ensembl for SV variants when genome build 38.
- Arrange information in columns on variant page
- Fix so that new cosmic identifier (COSV) is also acceptable #1304
- Fixed COSMIC tag in INFO (outside of CSQ) to be parses as well with `&` splitter.
- COSMIC stub URL changed to https://cancer.sanger.ac.uk/cosmic/search?q= instead.
- Updated to a version of IGV where bigBed tracks are visualized correctly
- Clinvar submission files are named according to the content (variant_data and case_data)
- Always show causatives from other cases in case overview
- Correct disease associations for gene symbol aliases that exist as separate genes
- Re-add "custom annotations" for SV variants
- The override ClinVar P/LP add-in in the Clinical Filter failed for new CSQ strings

### Changed
- Runs all CI checks in github actions

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
- Adds test files for merged somatic SV and CNV; as well as merged SNV, and INDEL part of #1279
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
