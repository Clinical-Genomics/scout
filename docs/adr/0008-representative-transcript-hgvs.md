# Representative transcript and the HGVS reference sequence

- **Status:** Accepted
- **Date:** 2026-11-23
- **References:** #6070, #6617, #5246, #6737

## Context

Summaries, reports and brief displays show the HGVS of one transcript per gene. The choice used to
be made separately in several places, with different rules for rare disease and cancer. GRCh38
variants have MANE annotation; GRCh37 variants do not, but are often annotated on RefSeq
transcripts directly, for example by MIP or early nf-core/raredisease versions.

## Decision

- One shared picker, `get_representative_transcript`, selects transcripts in this order: gene
  panel disease-associated transcript, MANE Select, MANE Plus Clinical, HGNC primary RefSeq
  transcript, VEP canonical, any transcript with a RefSeq id, then the first annotated transcript.
  A transcript chosen by a lab in a gene panel takes precedence over MANE.
- HGVS is given on the transcript it was annotated on, whether Ensembl (`ENST…`) or a RefSeq
  transcript annotated directly (`NM_…`). An Ensembl transcript is shown under its RefSeq
  accession only when the two form a MANE pair, which guarantees identical sequences. Other
  Ensembl-to-RefSeq matches are shown alongside the HGVS, never used as its reference, to avoid
  mapping errors.
- Directly annotated RefSeq transcripts are matched to HGNC primary and panel transcripts
  ignoring the version number.

## Consequences

On GRCh37, Ensembl-annotated variants get `ENST…:c.` descriptions, while RefSeq-annotated variants
get `NM_…:c.`. On the variants list pages, genes are not decorated with HGNC primary and gene panel
transcript information, so the brief HGVS there can come from a different transcript than on the
variant page. This is accepted for now and left to a later change, since the display there depends
on the selected gene panels.
