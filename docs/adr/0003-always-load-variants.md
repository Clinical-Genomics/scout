# Some variants are always loaded, whatever the rank score threshold

- **Status:** Accepted
- **Date:** 2019-10-11 (ClinVar); managed variants 2020-10-01; causatives in other cases 2023-10-04
- **References:** #1105, #1317, #1379, #2065, #4087, #4090, #5922, #5924

## Context

Variants are only loaded above a rank score threshold, to avoid clogging the database with
millions of variants. Known pathogenic variants with a low rank score, such as founder,
reduced-penetrance or non-exonic variants, would then be missed.

## Decision

`MongoAdapter._load_variants` (`scout/adapter/mongo/variant_loader.py`) loads a variant when any
of these holds, checked lazily in this order:

- it has no rank score, or its rank score is above the threshold
- it is mitochondrial
- it is an STR
- it is ClinVar pathogenic, likely pathogenic or conflicting (`is_pathogenic`)
- it matches a managed variant (`_is_managed`)
- it is causative in another case (`_is_causative_other_cases`)

## Consequences

- The ClinVar rule ensures that odd pathogenic variants are not overlooked on load, and frees the
  rank model from having to catch them (#1317). The terms were limited to P, LP and conflicting,
  not "everything except benign".
- Managed variants (#1105) were chosen as an editable list in Scout over pushing the problem
  upstream to the rank models.
- Causatives from other cases overlap with ClinVar, but are kept because of the delay before
  ClinVar annotates a new causative (#4087).
- Managed and causative lookups are cached once per load, which cut load time about 8–10 times
  (#5924).
- Why MT and STR variants are always loaded is not recorded.
- Described for admins in [Loading variants](../admin-guide/loading-variants.md).
