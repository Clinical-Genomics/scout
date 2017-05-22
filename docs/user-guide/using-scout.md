# Pinning a variant
If you find a variant that seems interesting enough that you believe someone should follow it up, you could consider "pinning it" to the case. This means that it will show up for all users to see in the case view along other pinned variants.

A variant can be pinned by anyone and likewise unpinned by anyone (not just the person who originally pinned it). The activity log will store records of who did what for future reference, however.

# Mark Causative
A variant is marked causative when it is confirmed to be disease causing in a case. The variant will show up on the [case](cases.md) page as causative variant. A case can have multiple causative variants.
When a variant is marked causative, Scout will remember the variant so when when entering a new case Scout will indicate if a variant that was previously marked causative within the same institute exists in the particular case.


# Sending Sanger email
It's possible to send an email to a user defined email address with information regarding a variant for Sanger validation. You can access this functionality through the variant detail view in the upper right ahnd corner.

# Local Frequency Database
This is not really a local *frequency* database but rather an indication if we have seen a variant before and in what form. It should work as a guide to exclude variants that exists due to artifacts in the sequencing process or if it as been observed in any of the earlier cases.
Variants are added to the database in the following way:

- For each case we pick one affected individual
- Variants are filtered out based on if they are common or have a very low call quality
- The remaining variants are stored in loqusdb

Each time the user looks at a variant scout will ask locusdb how many times it has been seen across *all* cases from all institutes (obs.), how many times it has been seen in a homozygous state (homo.) and how many cases these numbers are based on (tot.).