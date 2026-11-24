# Code style and changelog: Black at line length 100, isort, and a changelog entry per PR

- **Status:** Accepted
- **Date:** 2019-10-04 (line length 100); Black 2020-02-04; changelog check 2020-09-04; isort 2021-04-15
- **References:** #1362, #1683, #2074

## Context

Contributors from several sites work on the same code base, and releases need a readable record
of what changed.

## Decision

- Code is formatted with Black at line length 100 and isort with the `black` profile
  (`[tool.black]` and `[tool.isort]` in `pyproject.toml`). CI (`linting_only.yml`) checks Black,
  isort and a limited flake8 selection.
- `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com), with an `[unreleased]`
  section and Added, Changed and Fixed headings. Each entry ends with its PR number.
- `keep_a_changelog.yml` fails PRs that don't touch the `unreleased` section. Hotfixes can skip
  it with the `Skip-Changelog` label.

## Consequences

- The Black version is deliberately not pinned, so as not to miss updates and bug fixes. Small
  formatting differences between Black versions are accepted (#1683).
- Ruff is in the lint dependency group but not enforced in CI.
- An arbitrary line length of 100 rather than Black's default 88 was chosen to reduce the number
  of lines slightly, while still being very readable in multiple columns on a modern monitor.
