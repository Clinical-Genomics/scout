# Variant ids: a case-specific document id and a case-independent variant id

- **Status:** Accepted
- **Date:** 2016-10-06 (recorded retrospectively; md5 keys date back to 2014)
- **References:** #2584, #2615, #2661

## Context

Variant documents need a primary key that is unique per case. Many features also need to find
"the same variant" in other cases: dismissals, causatives in other cases, managed variants and
events. REF and ALT can be very long strings, so they are hashed rather than used verbatim.

## Decision

`parse_ids` in `scout/parse/variant/ids.py` builds four ids. The hashed ones use
`generate_md5_key` (`scout/utils/md5.py`) on the space-joined fields:

- `simple_id`: `chrom_pos_ref_alt`, human readable and not unique.
- `display_name`: `chrom_pos_ref_alt_variant_type`.
- `variant_id`: md5 of chrom, pos, ref, alt and variant type (`clinical` or `research`). The same
  in every case.
- `document_id`: md5 of the same fields plus `case_id`. Used as the MongoDB `_id`, so each case
  has its own variant document.

Only the first ALT is used. STRs without an ALT get `.`.

## Consequences

- Cross-case lookups, such as dismissals and causatives in other cases, use the indexed
  `variant_id`.
- Because the variant type is part of the id, a position has different ids as a clinical and as a
  research variant. Code that needs both computes both; managed variants always hash as
  `clinical`.
- Genome build, END and category are not part of the id.
- Accepted limitation: SVs with the same start and a symbolic ALT (`<DEL>`, `<DUP>`) but a
  different END get the same id, and only one is kept. Adding END to the id would need a full
  repopulation of the database and changes to all internal and external lookups (#2615), so
  #2661 only added a warning. Overlapping SVs are expected to be merged upstream, for example by
  svdb.
- Why the variant type, rather than e.g. genome build, is part of `variant_id` is not recorded.
