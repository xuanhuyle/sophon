# held_out

Scorer-only material. Solver arms must never read this directory; during solver runs it is encrypted.

- `oracle/`: OpenFisca-France parameter files (independent encoding of the same law).
- `maintainers/`: what the mon-entreprise maintainers actually committed later. Not gold.
- `REFERENCE.json`, `COVERAGE.json`: written by `src/build_reference.py` from the article texts before any solver run.
