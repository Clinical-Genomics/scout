# FAQ

## My email has been added as a Scout user, but I can't log into Scout

There are several login systems possible, as configured by your admin.

In Solna, we use Google to authenticate users. This may be a little confusing if you already use Google for other purposes, such as email or web searches.
You can be logged into multiple Google accounts at the same time. If you are only logged into
one account, it will automatically be used when you click "Login with Google".

Visit [Google][google] and click your avatar in the top right corner and "Add account" and log with your Scout connected account. Next time you access Scout you will be presented with an option of which Google account to use.


## What should my VCF format look like in detail?

Scout supports standard genomics file formats in general, and will work to some degree with many a generic (ideally VEP annotated) VCF as input, but, if you have a choice, for best results out of the box, use an already well integrated pipeline.
The most well tested pipelines for Scout viewing currently are [MIP](https://github.com/Clinical-Genomics/MIP) (RD SR) or [Nextflow-wgs](https://github.com/Clinical-Genomics-Lund/nextflow_wgs) (RD SR),
[Balsamic](https://github.com/Clinical-Genomics/BALSAMIC) (somatic), [nf-core/RNAfusion](https://github.com/nf-core/rnafusion) (RNA fusion) and [tomte](https://github.com/genomic-medicine-sweden/tomte) (RNA expression)
We fully support [nf-core/raredisease](https://github.com/nf-core/raredisease) and [nf-core/Nallo](https://github.com/genomic-medicine-sweden/nallo) (RD LRS). We also
have compatibility with at least earlier versions of other pipelines e.g. [sarek](https://github.com/nf-core/sarek) (somatic), https://github.com/J35P312/FindSV (RD SVs) and [poorpipe](https://github.com/J35P312/poorpipe) (RD LRS),
and yet others through compatibility layers that add a baseline of VEP annotation and ranking, e.g. [scout-annotation](https://github.com/gmc-norr/scout-annotation), [oncorefiner](https://github.com/Clinical-Genomics/oncorefiner).

To use the full features of Scout, try to load pre-ranked variants (see [genmod](https://github.com/Clinical-Genomics/genmod)).
An important take home for variant triage, especially of SVs, is that you need to get good local database frequency annotation going. We use [SVDB](https://github.com/J35P312/SVDB) and/or [loqusdb](https://github.com/Clinical-Genomics/loqusdb).

Say hi to the developers in a GitHub issue or discussion, describe your pipeline and situation, and we may be able to direct you.

## Wouldn't it be great if you could just click a variant table column header to sort the table by that column?

Rest assured you are not the first to suggest it. Scout displays variants sorted by a rank score. This is intentional, encouraging the user to focus on the most likely causal variants first.
You can however filter the variants by selecting options on the filter panel which usually solves the intended use case.
You are encouraged to save and reuse your filter settings as a named custom filter, and you can use the "Audit filter" function to log the investigation to the case audit log.
If you are missing a filter option, please open a GitHub issue or discussion and we will consider adding it.


[google]: https://www.google.com
