# Publication completion report for v1.0.0

**Completed:** 2026-08-05 12:08:07 JST  
**Repository:** https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry  
**Result:** `PASS`

## Git and release identity

- Release/tag-time `main` commit:
  `a7ac5663eac2608e19a75d6e5baa0644389511e8`
- Annotated tag object:
  `43ca85915964fabd162c8c4e2f56ee6dc9bb736e`
- `v1.0.0` tag commit:
  `a7ac5663eac2608e19a75d6e5baa0644389511e8`
- Release:
  https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/releases/tag/v1.0.0
- Release state: published; not a draft; not a prerelease.

The public repository uses `main` as its default branch. The remote and local
release/tag-time commit IDs matched. No force push was used.

## GitHub Actions

- Workflow: `tests`
- Tag-triggered run:
  https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/actions/runs/30971199043
- Status: `completed / success`
- Head SHA: `a7ac5663eac2608e19a75d6e5baa0644389511e8`

The earlier main-push run also completed successfully:
https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/actions/runs/30971113646

## Verification summary

- Frozen tests: 45/45 passed locally and in GitHub Actions.
- Scientific result audit: all requested values matched frozen CSVs; mismatch 0.
- 50,000-bootstrap reproduction: five tables, 59 total rows, exact match.
- Relative Markdown links: 52 checked, 0 broken.
- Secret patterns: 0.
- Concrete private Mac paths: 0.
- `sandbox:/mnt/data` links: 0.
- ChatGPT internal file IDs: 0.
- CFF YAML parse: passed.
- Published repository: public.
- Default branch: `main`.
- Repository topics: all 9 requested topics present.
- GitHub root-license recognition: Apache License 2.0.

## License mapping

- Code (`src/`, `scripts/`, `tests/`, Python configuration, CI, and
  reproduction code): Apache License 2.0 in `LICENSE`.
- Data, manifests, processed/analysis CSV files, execution receipts, and
  published result tables: CC BY 4.0 in `LICENSE-DATA`.
- Manuscript, supplement, documentation, figures, README files, and protocol
  documents: CC BY 4.0 in `LICENSE-DOCS`.
- Third-party material remains subject to its own rights and licenses.

All three installed license files matched the official plain-text license
documents byte-for-byte during pre-publication verification.

## Citation status

`CITATION.cff` parsed successfully and is present on the default branch. It
contains the title, message, software type, repository URLs, v1.0.0 release
date and version, Apache-2.0 code license, and the confirmed Unicode author name
竹内 琉瑛. No English transliteration was inferred.

## Release assets

| Asset | Published SHA-256 |
|---|---|
| `PaperB_public_release_all_in_one_2026-08-05_v1_0.zip` | `98be5f2380a74548d3b0cb50e02e28f92b300f46312321973ea9c54d04a00704` |
| `PaperB_public_release_all_in_one_2026-08-05_v1_0.zip.sha256` | `477bf520edd8df896bdfc82cf2b0e57b01a1954f10116923ecb8a23af6c0cdcb` |
| `PaperB_legacy_mvp_versions_v0_1_to_v0_14_clean_2026-08-05.zip` | `0d7c4cdcdaa9ecc40ce4d22e141b5622050d996ac2c4a83b3b7cab9f4226b1b2` |
| `PaperB_legacy_mvp_versions_v0_1_to_v0_14_clean_2026-08-05.zip.sha256` | `85b7abf69c6c8a706cf3ae85a3d5da10218acb1c1b184682dec52877f6439ff5` |

The four assets were downloaded again after publication. Their bytes matched
the GitHub-provided digests and the two sidecars declared the expected ZIP
hashes. Both ZIP archives passed compressed-data integrity testing. The absent
core ZIP was not reconstructed.

## Scientific-content preservation

**Scientific files changed: 0.** Confirmatory results, endpoint, SESOI, verdict
rule, manifests, yoke map, frozen protocol, frozen source behavior, merged
confirmatory CSV, bootstrap settings, receipts, claim boundary, and the
confirmatory/development distinction were not changed.

The English DOCX changed only in its Code and Data Availability paragraphs.
The Japanese DOCX changed only in the corresponding Availability paragraph.
All 32 English pages, 20 Japanese pages, and 7 supplementary pages passed the
render audit. The supplementary DOCX remained byte-identical.

## Known limitations and non-blocking future metadata

- ORCID
- Affiliation
- Article DOI
- Repository archive DOI
- Peer-review and journal-submission information

The released figure files are preserved, but their generation source was not
available and was not inferred. Full step-level traces are not stored in Git
history; the frozen code and manifests required to regenerate them are
provided. Legacy v0.14 is a historical baseline, not the canonical
confirmatory implementation.
