# Brief HGVS shows p. for protein-altering variants, c. otherwise

- **Status:** Accepted
- **Date:** 2026-11-23
- **References:** #6070, #6737

## Context

Compact displays, such as variant names in lists, links and the activity panel, have room for one
HGVS description.

## Decision

Show the protein change (p.) for protein-altering consequences: missense, stop gained, stop lost,
start lost, frameshift, inframe insertions and deletions, and protein altering. Show the coding
change (c.) for all other consequences, including synonymous, splicing, intronic and UTR variants,
or when no p. is annotated.

## Consequences

One helper, `get_brief_hgvs`, decides this for every brief display.
