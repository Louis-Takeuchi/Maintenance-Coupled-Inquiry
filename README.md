# Maintenance-Coupled Inquiry

A preregistered computational experiment testing whether component-aligned maintenance signals alter evidence allocation, causal diagnosis, and replicated restoration under finite inquiry budgets.

**Repository status:** Public-release candidate  
**Version:** 1.0.0  
**Paper status:** Manuscript prepared; not yet published  
**License status:** Not yet selected; no open license is currently granted  
**Latest release:** [Planned versioned release](https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/releases/latest)  
**日本語:** [README_ja.md](README_ja.md)

## Scope and claim boundary

This repository reports a functional computational experiment in a constrained
causal microworld. It supports the following limited findings:

- component-aligned maintenance signals changed evidence allocation;
- `actual_need` outperformed a `yoked_need` control that preserved total need
  while disrupting component alignment;
- replicated restoration improved under actual need;
- evidence-trace differences remained under a common decoder that received
  neither condition identity nor need vectors; and
- actual need passed the prespecified neutral-world false-repair safety gate.

It does **not** establish constitutive autonomy, endogenous normativity,
constitutive death, biological individuality, a general autonomous scientist,
or human-level cognition. Need variables, viable ranges, damage, repair,
intervention vocabulary, and stopping rules remain designer specified. See
[CLAIM_BOUNDARY.md](docs/CLAIM_BOUNDARY.md).

## Main confirmatory results

Values below were cross-checked against the frozen CSV outputs and integrity
audit, not transcribed from memory.

| Measure | Frozen result |
|---|---:|
| Confirmatory seeds | 72 |
| Primary source runs | 576 |
| Ablation source runs | 432 |
| Exact replay | 288/288 |
| Target sensing difference, actual − yoked | +0.1173 |
| 95% stratified paired bootstrap CI | [+0.0722, +0.1632] |
| Prespecified SESOI | +0.08 |
| Actual replicated restoration | 41/72 |
| Yoked replicated restoration | 20/72 |
| Paired difference | +0.2917 |
| Neutral-world actual false repair | 0/72 |
| One-sided 95% exact upper bound | 0.0408 |

The actual condition did not succeed in every world; replicated restoration was
41/72. The supported claim is a probabilistic improvement over the yoked
control, not perfect or general causal competence. See
[RESULT_SUMMARY.md](docs/RESULT_SUMMARY.md).

## Repository map

| Path | Role |
|---|---|
| [`manuscript/`](manuscript/) | Markdown manuscript (public-link canonical copy), DOCX snapshot, and machine-readable tables |
| [`supplement/`](supplement/) | Supplementary Markdown and DOCX snapshot |
| [`figures/`](figures/) | Released paper and supplement figures in PDF and PNG |
| [`protocol/`](protocol/) | Frozen confirmatory protocol and freeze-readiness evidence |
| [`src/`](src/) | Byte-preserved frozen v0.3 Python package |
| [`scripts/`](scripts/) | Frozen runners, archived post-run analysis, and public verification helpers |
| [`tests/`](tests/) | Frozen unit tests |
| [`manifests/`](manifests/) | Seed, yoke, chunk, endpoint, SESOI, activation, and freeze manifests |
| [`data/processed/`](data/processed/) | Merged primary and ablation confirmatory data |
| [`data/analysis/`](data/analysis/) | Endpoint, common-decoder, ablation, verdict, and summary outputs |
| [`data/execution_receipts/`](data/execution_receipts/) | All 120 immutable execution receipts |
| [`docs/development/`](docs/development/) | Development-phase and repository-audit records |
| [`legacy/`](legacy/) | Historical v0.14 pre-unification baseline, not the paper implementation |

See [FILE_MAP.md](docs/FILE_MAP.md) for canonical-source and generated-output
relationships.

## Quick start

The frozen package declares Python **3.11 or later** and has no runtime
third-party dependencies. Pytest is required for the test suite.

```bash
git clone https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry.git
cd Maintenance-Coupled-Inquiry
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
python scripts/verify_public_results.py
```

The frozen suite contains 45 tests. The verification helper is read-only and
checks the published run counts and headline values against the CSV outputs.

## Reproducing the analysis

To regenerate the principal endpoint, common-decoder, and ablation tables into
an ignored build directory without overwriting the frozen outputs:

```bash
python scripts/reproduce_processed_analysis.py --output build/reproduced-analysis
python scripts/compare_reproduced_analysis.py build/reproduced-analysis
```

The inputs are the merged files in `data/processed/`. The archived original
post-run scripts are retained byte-for-byte in `scripts/archived_postrun/`;
they contain the original `/mnt/data/paperB-unified-v1` container path and are
preserved as provenance rather than silently rewritten.

No figure-generation source script was present in the supplied public package.
The released PDF/PNG figures are available in `figures/`, but exact figure
regeneration from code cannot currently be claimed. This is recorded as an open
reproducibility limitation.

Analysis-only reproduction reads existing merged summaries and runs the fixed
50,000-replicate bootstrap. Full confirmatory reproduction instead executes
1,008 source runs plus 288 replay cases and requires the frozen activation,
chunk, seed, and yoke manifests. Do not edit those manifests. Review
[REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) before attempting a full run.

## Data availability

Git tracks the merged primary and ablation run summaries, endpoint tables,
analysis outputs, integrity audits, and execution receipts. Versioned Release
assets are planned for the all-in-one package, core package, and cleaned legacy
archive.

Full step-level traces are **not** included in the main Git history or current
validated package. A previous full-trace ZIP failed archive-integrity checking
and was excluded. The frozen code and manifests required to regenerate traces
are provided; a fresh validated trace deposit is still required before claiming
that every raw step trace is public.

## Historical versions

v0.14 is preserved as a historical pre-unification baseline. It did not
generate the final confirmatory results and must not be treated as the canonical
implementation of the paper.

Versions v0.1–v0.13 are development provenance, not the main implementation.
Their cleaned archive is planned as a Release asset rather than part of the main
tree. See [LEGACY_VERSIONS.md](docs/LEGACY_VERSIONS.md).

## Citation

See [`CITATION.cff`](CITATION.cff) and the manuscript title in
[`manuscript/`](manuscript/). The paper is unpublished, and no journal volume,
issue, pages, article DOI, or archive DOI has been assigned here. Author and
license fields remain unresolved in
[`PUBLICATION_OPEN_FIELDS.md`](PUBLICATION_OPEN_FIELDS.md); complete them before
publishing the release.

## AI assistance disclosure

OpenAI ChatGPT assisted with English translation, structural editing, and
document formatting. The author reviewed and verified the scientific claims,
calculations, references, and final wording and remains responsible for the
content. This repository does not claim that AI autonomously made research
decisions or ran the confirmatory experiment without human oversight.

## License

No open licenses are active yet.

| Material | Current status | Candidate decision |
|---|---|---|
| Code | No license granted | MIT or Apache-2.0 |
| Data | No license granted | CC0 1.0 or CC BY 4.0 |
| Manuscript, docs, figures | No license granted | CC BY 4.0 |

Do not infer permission from public visibility. See `LICENSE`, `LICENSE-DATA`,
`LICENSE-DOCS`, and `PUBLICATION_OPEN_FIELDS.md`.

