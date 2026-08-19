## What's new in 4.114?

_Posted: Aug 19 2026_

Scout 4.114 welcomes you back after a summer hiatus.

After a few short outages of UCSC downloads and GitHub that affected IGV.js availability, we have made the location of some more
reference files configurable in the Scout. In particular, reference genomes can now be locally served if need be.

*Note* that current ClinVar germline submissions will be made *obsolete* in the next update, so please make sure to close any open submissions before then.

### Highlights

- It is now time to migrate to the new ClinVar germline submissions format, introduced in January. The submissions
for germline variants will be done in the same way as somatic variants, directly from Scout to the ClinVar API, and the pages
have got several improvements in the process. To fully adopt the new submission format, we will need to *close open submissions* of the old format. You have until the next update (two to three weeks) to close any open submissions.
The submissions will still be shown as legacy submissions in Scout, but you will not be able to submit them to ClinVar anymore. You could of course still add the same variants to a
new submission after the update, so no stress.
- Inheritance patterns are shown on genes on the OMICS outliers page.

### Also included
- Pagination on the ClinVar germline submissions page
- Dark regions genes are shown as a category on the gene panel extent report, replacing the SMN only one.
The extent report now also has an option to hide case specific identifiers, such as case ID and dates. This would potentially enable
reuse of reports for other cases, but be aware that the extent report will still be tailored to the specific case.

