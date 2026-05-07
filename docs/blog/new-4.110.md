# What's new in Scout v4.110.0?

_Posted: Apr 24, 2026_

Dear users and admins,

✨🌸 We have a shiny spring Scout release for you today, v4.110.0.

✨The main features include loading and display of Paraphrase parsed Paraphase calls from long read sequencing, renaming the `SMN` button to `SMN - Dark regions`. In Solna, be advised these will not start loading until after the next Nallo and CG updates.

🛠️ Between version 4.107 (released 260113) and this release, there has been an unintended lifting of the singleton exception to the "Include variants present only in unaffected” variants filter.
This meant that variants that were not explicitly genotyped for the singleton individual, such as inconclusive “.”/“./.” STR and SV calls, were not shown in searches, unless the "Include variants present only in unaffected” option was used. We are aware of a small number of WES GATK DUPs and for WGS, small, noisy region TIDDIT de novo assembly BNDs. Please consider if you have cases impacted where you relied on the exception and recheck these, either after the update or simply now with the "Include variants present only in unaffected” option toggled on.

Note that this is the standard mode of operation for cases with more than one individual. In order to hide unaffected carrier status from incidental discovery, variants like these are not displayed unless the checkbox is ticked.

Institutes who use the always-on option for “Include variants present only in unaffected” have not been affected.

⚙️Admins, note some new options have been added to make export of causatives, verified and managed variants easier and more similar.
