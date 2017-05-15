## What's new in 3.1?

_Posted: 27 April 2017_

This updates contains many bug fixes and a few new features.

### New feature: cohort tag

We have introduced "cohort tags", where you can tag each case as belonging to one or several cohorts.

Future release of Scout will include functionality to get statistics on selected cohorts or all cases. For instance, you will be able to get statistics on the number of samples within a cohort, how many are cases solved and which genes there were causative variants in. Or perhaps you want to know which phenotype terms are associated with a particular cohort.

For now, the cohort tags are _specific_ to CMMS, but we urge all user to supply to us their own set of tags to be used within the corresponding Scout instance. This applies to **phenotype groups** as well as we think this will be very useful in future to describe your cohorts clinically.

### New feature: pip distribution

Scout is now installable via `pip`! This means installing the server and CLI is as simple as running:

```bash
pip install scout-browser
```

Everything to setup the server; genes, HPO terms, OMIM information, etc. is included in the distribution.

### Bug fixes

- Compounds are now sorted on combined score
- The delivery report opens in a new tab
- A link from the variant page to the gene panel exists
- Cases are properly activated when variants are first viewed
- Fixed display of HGVS description
- Fixed issues with Sanger email
- Support for a new analysis type: TGA, Targeted Genome Analysis
- Fixed issue with filtering on 1000G frequency
