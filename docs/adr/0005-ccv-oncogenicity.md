# Separate ClinGen-CGC-VICC oncogenicity classification for cancer variants

- **Status:** Accepted
- **Date:** 2024-12-03
- **References:** #4967, #5069, #5629, #6369

## Context

Labs asked for oncogenicity classification of somatic variants following Horak et al. 2022
(#4967). The ACMG rare disease guidelines are not recommended for somatic variants, but a cancer
variant may occasionally need evaluation as a potential germline variant.

## Decision

- ClinGen-CGC-VICC (CCV) is a classification of its own, with its logic in `scout/utils/ccv.py`
  (`get_ccv_points`, `get_ccv`, `get_ccv_temperature`, `get_ccv_conflicts`). The class is given
  directly by the points: oncogenic ≥ 10, likely oncogenic 6–9, VUS 0–5, likely benign -1 to -6,
  benign ≤ -7.
- Evaluations are stored in their own collection (`scout/adapter/mongo/ccv.py`), and the variant
  gets a `ccv_classification`.
- The CCV form is shown only for cancer cases. The ACMG form stays available on cancer variants.

## Consequences

- A cancer variant can have both an ACMG and a CCV classification, and reports must handle both.
- CCV follows the ACMG features: case reports, ClinVar oncogenicity submissions and criteria
  modifiers. Conflict rules were aligned with Horak et al. in #5629.
