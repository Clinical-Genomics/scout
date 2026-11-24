# Look up variants by id separately from the filtered variants query

- **Status:** Accepted
- **Date:** 2026-11-23
- **References:** #6736, #6738

## Context

`variants()` builds the filtered, sorted and paged query behind the variants pages. It also
accepted a list of `variant_ids`, but no code used that option, while code that needed variants by
id wrote its own queries or fetched them one at a time.

## Decision

`variants()` is only for filtered variant lists. Fetching a case's variants by `variant_id`, of any
category, goes through `case_variants_by_variant_ids()`.

## Consequences

Callers with a set of ids, such as events and comments, use one indexed query on `variant_id` and
`case_id` instead of one query per variant.
