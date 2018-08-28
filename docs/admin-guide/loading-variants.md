# Variant loading

This document will describe the process of variant loading, how it is done and why.

## Rank Score

In Scout rank score is a central theme. Rank Scores is a estimation on how potentially dangerous a variant is, similar to the CADD score with the intention of work with all types of variation. 
The uploading of variants is based on a rank score threshold, this is to avoid to clog the database with millions of variants that we at the moment have a hard time to say anything about.

The rank score is a summary of the annotations of a variant. Rank scores are calculated and annotated by [GENMOD][genmod]

[genmod]: https://github.com/moonso/genmod
