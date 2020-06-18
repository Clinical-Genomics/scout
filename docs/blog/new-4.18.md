## What's new in 4.18? 🍁

_Posted: 18 Jun 2020_

One of the most important changes introduced in this version is that we have switched from a Google login system based on Flask-OAuthlib to Authlib libraries.
In order to support the new login system Scout administrators would need to modify the config settings as described in this updated [guide](https://github.com/Clinical-Genomics/scout/blob/master/docs/admin-guide/login-system.md).


This is a complete list of all changes introduced in this new release:

## [4.18]

## New features
- Filter cancer variants on cytoband coordinates
- Show dismiss reasons in a badge with hover for clinical variants
- Show an ellipsis if 10 cases or more to display with loqusdb matches
- A new blog post for version 4.17
- Tooltip to better describe Tumor and Normal columns in cancer variants
- Filter cancer SNVs and SVs by chromosome coordinates
- Default export of `Assertion method citation` to clinVar variants submission file
- Button to export up to 500 cancer variants, filtered or not
- Rename samples of a clinVar submission file

## Bugfixes
- Apply default gene panel on return to cancer variantS from variant view
- Revert to certificate checking when asking for Chanjo reports
- `scout download everything` command failing while downloading HPO terms

### Changes
- Turn tumor and normal allelic fraction to decimal numbers in tumor variants page
- Moved clinVar submissions code to the institutes blueprints
- Changed name of clinVar export files to FILENAME.Variant.csv and FILENAME.CaseData.csv
- Switched Google login libraries from Flask-OAuthlib to Authlib
