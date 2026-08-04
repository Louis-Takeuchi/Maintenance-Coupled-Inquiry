# Contributing

This repository preserves a frozen confirmatory experiment. Please use GitHub
issues for reproducibility problems, broken links, documentation corrections,
or proposed portability improvements.

Do not submit changes that silently alter confirmatory values, endpoints,
SESOIs, decision rules, seeds, yoke mappings, protocol files, frozen source
behavior, merged data, or execution receipts. A scientifically meaningful
change requires a new protocol/version, explicit provenance, and new outputs;
it must not overwrite the v0.3 record.

Before proposing a change, run:

```bash
python -m pip install -r requirements.txt
pytest -q
python scripts/verify_public_results.py
git diff --check
```

