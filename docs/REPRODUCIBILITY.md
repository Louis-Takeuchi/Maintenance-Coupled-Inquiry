# Reproducibility guide

## Environment

- Python: 3.11 or later (`pyproject.toml`)
- Runtime dependencies: none outside the Python standard library
- Test dependency: pytest 8.x or 9.x (`requirements.txt`)
- Frozen code version: 0.3.0
- Public repository release candidate: 1.0.0

The public tree reorganizes files for navigation. Files copied from the frozen
release retain their bytes; public helper scripts are not part of the frozen
implementation.

## Dependency installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Tests

```bash
pytest -q
python scripts/verify_public_results.py
```

Expected results for this release are `45 passed` and `PASS public result
verification`. Pytest is configured to collect only `tests/`; the tests under
`legacy/` belong to the historical v0.14 package.

## Processed analysis reproduction

The portable public helper reads the frozen merged summaries and writes five
tables to an ignored directory:

```bash
python scripts/reproduce_processed_analysis.py \
  --output build/reproduced-analysis
python scripts/compare_reproduced_analysis.py \
  build/reproduced-analysis
```

It regenerates:

- `primary_endpoint_intervals.csv`
- `primary_condition_summary.csv`
- `common_decoder_diagnostics.csv`
- `ablation_condition_summary.csv`
- `ablation_paired_diagnostics.csv`

The helper imports the frozen bootstrap and paired-analysis functions, uses
bootstrap seed `941731` and 50,000 replicates, and never writes into
`data/analysis/`. The comparison command requires row-for-row equality with the
released tables.

The original post-run scripts remain unchanged in `scripts/archived_postrun/`.
They record the original `/mnt/data/paperB-unified-v1` container layout and are
preserved as provenance. The public portability helper changes only file
location handling and output isolation; it does not replace the frozen scripts.

## Figure reproduction

Released figures are provided as PDF and PNG in `figures/`. No figure-generation
source script was present in the supplied public package or local project
materials searched during publication preparation. Exact figure regeneration
from code is therefore unresolved. Do not claim that the figures are currently
code-reproducible; retain the released files and add the original generation
script in a future, separately audited update if it becomes available.

## Full experiment reproduction

Full reproduction is materially different from analysis-only reproduction. It
executes 48 primary chunks (`P000`–`P047`) and 72 ablation chunks
(`A000`–`A071`), producing 576 primary and 432 ablation source runs; the primary
outputs include 288 actual/yoked replay diagnostics.

The runner interface for one chunk is:

```bash
python scripts/run_unified_confirmation.py \
  --chunk-id P000 \
  --output-root build/full-confirmatory-run
```

Before any full rerun:

1. Read `protocol/PaperB_UNIFIED_CONFIRMATORY_PROTOCOL_CANDIDATE_v0_3.md`.
2. Verify the freeze and activation records in `manifests/`.
3. Use the existing chunk IDs, seeds, yoke map, endpoint registry, SESOIs, and
   decision rules without modification.
4. Write to a new output root. Never overwrite `data/processed/` or
   `data/analysis/`.
5. Retain a receipt for every chunk and perform the key-grid, replay, and hash
   audits before interpretation.

No wall-clock or hardware estimate was recorded in the supplied artifacts, so
none is invented here. The source workload is 1,008 runs plus replay processing,
and the final bootstrap uses 50,000 replicates. Plan compute and storage before
starting.

## Expected released outputs

- Primary merged rows: 576
- Ablation merged rows: 432
- Exact replay: 288/288
- Execution receipts: 120/120
- Frozen unit tests: 45/45
- Main mechanism verdict: supported
- Downstream replicated-restoration verdict: supported
- Neutral false repair: 0/72, one-sided 95% upper bound 0.0408

## Hash verification

For the all-in-one Release asset, download the ZIP and its adjacent `.sha256`
file, then run:

```bash
shasum -a 256 -c PaperB_public_release_all_in_one_2026-08-05_v1_0.zip.sha256
```

After extracting that asset, run `shasum -a 256 -c SHA256SUMS.txt` at its
release root. For the expanded v0.14 baseline in this repository:

```bash
cd legacy/constitutive_inquiry_mvp_v0_14
shasum -a 256 -c SHA256SUMS.txt
```

The GitHub-oriented tree changes paths, so the all-in-one package's root
`SHA256SUMS.txt` must not be misrepresented as a path manifest for this tree.
Use Git commit identity for the reorganized tree and the versioned asset hashes
recorded in `RELEASE_NOTES_v1.0.0.md` for archives.

## Known limitations

- Full step-level traces are not in the validated package or Git history.
- The earlier full-trace ZIP failed central-directory integrity and was excluded.
- Figure-generation source is unavailable.
- Author, DOI, and license metadata remain unresolved.
- Receipt output paths and archived post-run scripts retain the original
  container path as provenance.
- The repository does not establish constitutive autonomy or endogenous
  normativity.

