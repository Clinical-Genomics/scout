# Architecture decision records

Architecture decision records (ADRs) keep the reasoning behind design and behaviour choices in
Scout: what was decided, why, and what follows from it. They complement the
[CHANGELOG](https://github.com/Clinical-Genomics/scout/blob/main/CHANGELOG.md), which records
*what* changed, with the reasoning that is otherwise scattered over issues and pull requests.

## Records

| No. | Decision | Status |
| --- | --- | --- |
| [0001](0001-variant-ids.md) | Variant ids: a case-specific document id and a case-independent variant id | Accepted |
| [0002](0002-code-style-and-changelog.md) | Code style and changelog: Black at line length 100, isort, and a changelog entry per PR | Accepted |
| [0003](0003-always-load-variants.md) | Some variants are always loaded, whatever the rank score threshold | Accepted |
| [0004](0004-acmg-modifiers-and-points.md) | ACMG: rule-based classification, criteria strength modifiers, and Bayesian points alongside | Accepted |
| [0005](0005-ccv-oncogenicity.md) | Separate ClinGen-CGC-VICC oncogenicity classification for cancer variants | Accepted |
| [0006](0006-packaging-uv.md) | Packaging with pyproject.toml, uv and hatchling | Accepted |
| [0007](0007-login-and-user-whitelist.md) | Login: one external authentication method per instance, authorization by Scout's user list | Accepted |
| [0008](0008-representative-transcript-hgvs.md) | Representative transcript and the HGVS reference sequence | Accepted |
| [0009](0009-brief-hgvs.md) | Brief HGVS shows p. for protein-altering variants, c. otherwise | Accepted |
| [0010](0010-variants-by-id-lookup.md) | Look up variants by id separately from the filtered variants query | Accepted |

Records 0001–0007 were written retrospectively from issues, pull requests and the code. Where the
original reasoning was not written down, the record says so.

## Adding a record

Add a record when a change settles a question that is likely to come up again: a choice between
reasonable alternatives, a deliberate limitation, or a rule that code in several places must
follow.

1. Copy the [template](template.md) to `NNNN-short-title.md`, using the next free number.
2. Fill in status, date, references, context, decision and consequences. Keep it short.
3. Add the record to the table above and to the `nav` section of `mkdocs.yml`.

Records are not rewritten when a decision changes. Add a new record instead, and set the old
one's status to `Superseded by NNNN`.
