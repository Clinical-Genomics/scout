## What's new in 4.19? 🍁

_Posted: 8 July 2020_

The biggest difference from previous versions is a new institute page exposing in a clear way links to pages that before were a bit hidden in the structure of the portal. This will hopefully make the navigation more user friendly!

This is a complete list of all changes introduced in this new release:


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
