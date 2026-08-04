# Data directory

- `processed/`: merged primary and ablation confirmatory summaries and merge
  audits tracked in Git.
- `analysis/`: frozen endpoint, condition, common-decoder, ablation, verdict,
  and summary outputs.
- `audits/`: post-run integrity audit.
- `execution_receipts/`: 120 immutable chunk receipts.

Full step-level traces are not included. Receipt `/mnt/data/...` paths are
original container provenance and have not been normalized. Do not overwrite
the released CSVs when reproducing analyses; write to `build/` or another new
directory.

