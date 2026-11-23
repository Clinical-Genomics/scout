# Packaging with pyproject.toml, uv and hatchling

- **Status:** Accepted
- **Date:** 2024-12-17; Python 3.9 dropped 2025-10-29
- **References:** #5053, #5124, #5818

## Context

PyPI warned that the `scout-browser-<version>.tar.gz` source distribution name breaks PEP 625,
which requires the normalized name `scout_browser` (#5053). The old setuptools setup with a
version file produced that name. Later, Python 3.9 reached end of life.

## Decision

- The build backend is hatchling. Dependencies and the dev, docs and lint dependency groups live
  in `pyproject.toml`; `setup.py` and requirements files are gone.
- `uv.lock` is committed. CI runs `uv run --frozen`, and the Docker images build on uv's Python
  images.
- `requires-python = ">=3.10"`. `.python-version` sets the version used by all GitHub workflows
  and the Docker images.

## Consequences

- Installs in CI are faster (#5124).
- CI tests only the `.python-version` interpreter; support for older Python versions relies on
  care, such as avoiding newer syntax, rather than a test matrix.
- Why uv and hatchling were chosen over other PEP 625 compliant tools is not recorded.
