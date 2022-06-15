# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

About changelog [here](https://keepachangelog.com/en/1.0.0/)

## []
### Added
- Test for PanelApp panels loading
- `panel-umi` tag option when loading cancer analyses
### Changed
- Black text to make comments more visible in dark mode
- Loading PanelApp panels replaces pre-existing panels with same version
- Removed sidebar from Causatives page - navigation is available on the top bar for now
### Fixed
- Remove a:visited css style from all buttons
- Background color of `MIXED` sequencing type on cases page

## [4.55]
### Changed
- Represent different tumor samples as vials in cases page
- Option to force-update the OMIM panel
### Fixed
- Low tumor purity badge alignment in cancer samples table on cancer case view
- VariantS comment popovers reactivate on hover
- Updating database genes in build 37
- ACMG classification summary hidden by sticky navbar
- Logo backgrounds fixed to white on welcome page
- Visited links turn purple again
- Style of link buttons and dropdown menus
- Update KUH and GMS logos
- Link color for Managed variants

## [4.54]
### Added
- Dark mode, using browser/OS media preference
- Allow marking case as solved without defining causative variants
- Admin users can create missing beacon datasets from the institute's settings page
- GenCC links on gene and variant pages
- Deprecation warnings when launching the app using a .yaml config file or loading cases using .ped files
### Changed
- Improved HTML syntax in case report template
- Modified message displayed when variant rank stats could not be calculated
- Expanded instructions on how to test on CG development server (cg-vm1)
- Added more somatic variant callers (Balsamic v9 SNV, develop SV)
### Fixed
- Remove load demo case command from docker-compose.yml
- Text elements being split across pages in PDF reports
- Made login password field of type `password` in LDAP login form
- Gene panels HTML select in institute's settings page
- Bootstrap upgraded to version 5
- Fix some Sourcery and SonarCloud suggestions
- Escape special characters in case search on institute and dashboard pages
- Broken case PDF reports when no Madeline pedigree image can be created
- Removed text-white links style that were invisible in new pages style
- Variants pagination after pressing "Filter variants" or "Clinical filter"
- Layout of buttons Matchmaker submission panel (case page)
- Removing cases from Matchmaker (simplified code and fixed functionality)
- Reintroduce check for missing alignment files purged from server

## [4.53]
### Added
### Changed
- Point Alamut API key docs link to new API version
- Parse dbSNP id from ID only if it says "rs", else use VEP CSQ fields
- Removed MarkupSafe from the dependencies
### Fixed
- Reintroduced loading of SVs for demo case 643595
- Successful parse of FOUND_IN should avoid GATK caller default
- All vulnerabilities flagged by SonarCloud

## [4.52]
### Added
- Demo cancer case gets loaded together with demo RD case in demo instance
- Parse REVEL_score alongside REVEL_rankscore from csq field and display it on SNV variant page
- Rank score results now show the ranking range
- cDNA and protein changes displayed on institute causatives pages
- Optional SESSION_TIMEOUT_MINUTES configuration in app config files
- Script to convert old OMIM case format (list of integers) to new format (list of dictionaries)
- Additional check for user logged in status before serving alignment files
- Download .cgh files from cancer samples table on cancer case page
- Number of documents and date of last update on genes page
### Changed
- Verify user before redirecting to IGV alignments and sashimi plots
- Build case IGV tracks starting from case and variant objects instead of passing all params in a form
- Unfreeze Werkzeug lib since Flask_login v.0.6 with bugfix has been released
- Sort gene panels by name (panelS and variant page)
- Removed unused `server.blueprints.alignviewers.unindexed_remote_static` endpoint
- User sessions to check files served by `server.blueprints.alignviewers.rem