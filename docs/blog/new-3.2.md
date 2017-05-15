## What's new in 3.2?

_Posted: 3 May 2017_

### New feature: Frequency links

We have added several frequency resources links to the variant frequency table on the variants page.

- Beacon: enabled searches in the global beacon network

	> **Note**: this is only outgoing queries and does not expose any variants in Scout.

- GnomeAD: the new version of EXAC, which includes approximately 120,000 exomes and 15,000 genomes. We will include gnomeAD in the MIP analysis and the rank model in a future update, but the gnomeAD browser is available from Scout now.

- SweGen: frequencies from 1000 Swedish genomes sampled from the twin registry. Created by SciLifeLab.

- LocusDB family link: It is now possible to see in, which other families a variant in LocusDB were detected.

### New feature: Upload all variants for a region or a gene

We have done some work on the variant uploads for this release. This also means that we are now ready to accept requests to upload additional variants for a custom gene or a region. For now you can raise it by submitting a ticket in the ticketing system while we work out how to better integrate it in Scout.

### New feature: Upload new gene panel

You can now upload a new gene panel directly in Scout. You will need a semi-colon (`;`) separated file following the format:

```
HGNC_symbol;HGNC_IDnumber;Disease_associated_transcript;Genetic_disease_model;Reduced_penetrance;Mosaicism;Clinical_db_gene_annotation
ANKS6;26724;NM_173551.3;AR;;;PEDHEP
XPNPEP3;28052;NM_022098.3;AR;;;PEDHEP
DCDC2;18141;NM_016356.4;AR;;;PEDHEP
CLDN1;2032;NM_021101.4;AR;;;PEDHEP
...
```
