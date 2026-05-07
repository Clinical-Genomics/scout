## What's new in 4.111?

_Posted: May 7 2026_

Scout 4.111 is a focused release with improvements around panel handling, managed variants,
and Saltshaker support.

### Highlights

- **PanelApp workflow improvements:** You can now download all PanelApp panels to a file and
  also load/update `PANELAPP-GREEN` from a pre-downloaded file. This makes panel handling
  easier in controlled or offline-friendly workflows.
- **Better build-aware managed variant linking:** We improved matching and counters so managed
  variants follow the case genome build correctly. In practice, this gives more reliable linking
  of causative variants, including build 37 causatives viewed in build 38 contexts.
- **Saltshaker support for rare disease rollout:** Scout now supports loading custom MT
  Saltshaker HTML reports, and the Saltshaker update command was fixed. This prepares us to use
  Saltshaker with new rare disease cases as soon as pipeline automation is updated.

### Also included

- Better handling of conflicts and duplicates when uploading managed variants.
- Updated default hg38 gnomAD linkout to the `non_uk_biobank` subset.
- Case page quality-of-life update: empty case categories are now hidden dynamically.
- New command to remove loaded rank models. Old Nallo cases in Solna used the same URL for different rank models. This will help in updating these eventually.
