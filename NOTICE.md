# Notice and license scope

This repository reorganizes the byte-preserved contents of the Paper B public
reproducibility package into a GitHub-oriented tree. The frozen scientific
source, manifests, processed data, analysis outputs, receipts, manuscript
snapshot, figures, and historical v0.14 baseline are copied from the release
package. Public explanatory documents and portability helpers are clearly
separate from those frozen artifacts.

The following license mapping applies to material for which the repository
author holds the necessary rights:

- Code in `src/`, `scripts/`, and `tests/`, together with Python configuration,
  CI, and reproducibility code: Apache License 2.0 (`LICENSE`).
- Data, manifests, processed and analysis CSV files, execution receipts, and
  published result tables: Creative Commons Attribution 4.0 International
  (`LICENSE-DATA`).
- Manuscript, supplementary materials, documentation, figures, README files,
  and protocol documents: Creative Commons Attribution 4.0 International
  (`LICENSE-DOCS`).

Third-party materials remain subject to the rights of their respective owners
and to their own licenses. Bibliographic reference text and external
publications cited by this repository are not included as redistributed works.

The 120 execution receipts retain `/mnt/data/paperB-unified-v1/...` output paths
as execution provenance. Those paths identify the original container layout;
they are not current local paths or credentials.
