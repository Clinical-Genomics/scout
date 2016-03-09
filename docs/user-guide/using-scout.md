# Pinning a variant
If you find a variant that seems interesting enough that you believe someone should follow it up, you could consider "pinning it" to the case. This means that it will show up for all users to see in the case view along other pinned variants.

A variant can be pinned by anyone and likewise unpinned by anyone (not just the person who originally pinned it). The activity log will store records of who did what for future reference, however.

> In the future, we would also like to add the possibility of linking a confirmed disease causing mutation to a specific case. One could imagine that process to start of by suspecting a variant, pinning it, confirming the mutation, and lastly tagging it as disease causing. This would also allow us to build up a local database of conclusive findings which would be valuable on it's own.

# Sending Sanger email
It's possible to send an email to a user defined email address with information regarding a variant for Sanger validation. You can access this functionality through the variant detail view in the upper right ahnd corner.

# Local Frequency Database
This is not really a local *frequency* database but rather an indication if we have seen a variant before and in what form. It should work as a guide to exclude variants that exists due to artifacts in the sequencing process or if it as been observed in any of the earlier cases.
Variants are added to the database in the following way:

- For each case we pick one affected individual
- Variants are filtered out based on if they are common or have a very low call quality
- The remaining variants are stored in loqusdb

Each time the user looks at a variant scout will ask locusdb how many times it has been seen across *all* cases from all institutes (obs.), how many times it has been seen in a homozygous state (homo.) and how many cases these numbers are based on (tot.).