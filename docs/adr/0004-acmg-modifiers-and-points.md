# ACMG: rule-based classification, criteria strength modifiers, and Bayesian points alongside

- **Status:** Accepted
- **Date:** 2023-01-12 (modifiers); Bayesian points 2024-10-14
- **References:** #2463, #3753, #4646, #4909, #4920, #5157, #5297, #5871, #6561

## Context

Labs asked to downgrade or upgrade criteria such as PVS1 (#2463, following Abou Tayoun et al.
2018), which the plain Richards et al. 2015 rules cannot express. A points-based scale was also
requested, to rank VUS from cold to hot (#4909).

## Decision

- Criteria may carry a strength modifier in ClinGen SVI nomenclature: `_Stand-alone`,
  `_Very Strong`, `_Strong`, `_Moderate` or `_Supporting`, for example `PVS1_Moderate`.
  `get_acmg_criteria` (`scout/utils/acmg.py`) counts a modified criterion at its new strength.
  Unmodified criteria remain valid.
- The stored classification is always given by the Richards 2015 combination rules, `get_acmg`.
- Tavtigian et al. Bayesian points are computed by `get_acmg_temperature` and shown alongside,
  with a temperature for VUS. They are calculated when pages are rendered and not stored.

## Consequences

- The two classifications can disagree. Some modified combinations, such as several Very Strong
  criteria, have no Richards rule, while the points do reflect them. The variant page labels which
  classification is which (#6561), and the
  [ACMG user guide](../user-guide/acmg-criterias.md) explains the difference.
- Case reports respect modifiers (#5157).
- Why the rules, rather than the points, remain the stored classification is not recorded; points
  were introduced as an alternative to see how they are received (#4920).
