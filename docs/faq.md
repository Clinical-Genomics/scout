# FAQ

## My email is white listed but I can't log into Scout

You can be logged into multiple Google accounts at the same time. If you are only logged into
one account, it will automatically be used when you click "Login with Google".

Visit [Google][google] and click your avatar in the top right corner and "Add account" and log with your Scout connected account. Next time you access Scout you will be presented with an option of which Google account to use.


## What should my VCF format look like in detail?

Scout will work to some degree with many a generic (ideally VEP annotated) VCF as input, but, if you have a choice, for best results out of the box, use an already well integrated pipeline.
The most well tested pipelines for Scout viewing currently are [MIP](https://github.com/Clinical-Genomics/MIP) (RD SR) or [Nextflow-wgs](https://github.com/Clinical-Genomics-Lund/nextflow_wgs) (RD SR),
[Balsamic](https://github.com/Clinical-Genomics/BALSAMIC) (somatic), [nf-core/RNAfusion](https://github.com/nf-core/rnafusion) (RNA fusion) and [tomte](https://github.com/genomic-medicine-sweden/tomte) (RNA expression)
We fully support [nf-core/raredisease](https://github.com/nf-core/raredisease) and [nf-core/Nallo](https://github.com/genomic-medicine-sweden/nallo) (RD LRS). We also
have compatibility with at least earlier versions of other pipelines e.g. [sarek](https://github.com/nf-core/sarek) (somatic) and [poorpipe](https://github.com/J35P312/poorpipe) (RD LRS).

To use the full features of Scout, try to load pre-ranked variants (see [genmod](https://github.com/Clinical-Genomics/genmod)).
An important take home for variant triage, especially of SVs, is that you need to get good local database frequency annotation going. We use [SVDB](https://github.com/J35P312/SVDB) and/or [loqusdb](https://github.com/Clinical-Genomics/loqusdb).

Say hi to the developers in a GitHub issue or discussion, describe your pipeline and situation and we may be able to direct you.


[google]: https://www.google.com
