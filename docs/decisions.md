# Design decisions

A log of design and behaviour decisions in Scout: what was decided, why, and what follows from it.
It complements the [CHANGELOG](https://github.com/Clinical-Genomics/scout/blob/main/CHANGELOG.md),
which records *what* changed, with the reasoning that is otherwise scattered over issues and pull
requests.

Add an entry when a change settles a question that is likely to come up again: a choice between
reasonable alternatives, a deliberate limitation, or a rule that code in several places must
follow. Newest entries first. Earlier decisions are still to be back-populated.

Entry format:

```
## YYYY-MM-DD: Short title
**Status:** Accepted | Superseded by ... | Under discussion
**Context:** the problem and constraints
**Decision:** what we do
**Consequences:** what follows, including accepted limitations
**References:** issues and pull requests
```

---

## 2026-11-23: Look up variants by id separately from the filtered variants query

**Status:** Accepted

**Context:** `variants()` builds the filtered, sorted and paged query behind the variants pages. It
also accepted a list of `variant_ids`, but no code used that option, while code that needed
variants by id wrote its own queries or fetched them one at a time.

**Decision:** `variants()` is only for filtered variant lists. Fetching a case's variants by
`variant_id`, of any category, goes through `case_variants_by_variant_ids()`.

**Consequences:** Callers with a set of ids, such as events and comments, use one indexed query on
`variant_id` and `case_id` instead of one query per variant.

**References:** #6736, #6738

## 2026-11-23: Brief HGVS shows p. for protein-altering variants, c. otherwise

**Status:** Accepted

**Context:** Compact displays, such as variant names in lists, links and the activity panel, have
room for one HGVS description.

**Decision:** Show the protein change (p.) for protein-altering consequences: missense, stop
gained, stop lost, start lost, frameshift, inframe insertions and deletions, and protein altering.
Show the coding change (c.) for all other consequences, including synonymous, splicing, intronic
and UTR variants, or when no p. is annotated.

**Consequences:** One helper, `get_brief_hgvs`, decides this for every brief display.

**References:** #6070, #6737

## 2026-11-23: Representative transcript and the HGVS reference sequence

**Status:** Accepted

**Context:** Summaries, reports and brief displays show the HGVS of one transcript per gene. The
choice used to be made separately in several places, with different rules for rare disease and
cancer. GRCh38 variants have MANE annotation; GRCh37 variants do not, but are often annotated on
RefSeq transcripts directly, for example by MIP or early nf-core/raredisease versions.

**Decision:**

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

**Consequences:** On GRCh37, Ensembl-annotated variants get `ENST…:c.` descriptions, while
RefSeq-annotated variants get `NM_…:c.`. On the variants list pages, genes are not decorated with
HGNC primary and gene panel transcript information, so the brief HGVS there can come from a
different transcript than on the variant page. This is accepted for now and left to a later
change, since the display there depends on the selected gene panels.

**References:** #6070, #6617, #5246, #6737
