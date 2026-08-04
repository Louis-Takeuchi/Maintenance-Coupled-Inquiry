# Legacy versions

## v0.1–v0.13

These versions are development provenance. They document changes from easy
sanity baselines through structural generation, self-relevance, causal
abstention, composite interventions, and cross-world memory experiments. They
contain exploratory, superseded, positive, and negative results and must not be
pooled with or cited as the final confirmatory implementation.

The cleaned v0.1–v0.14 archive is planned as a versioned Release asset rather
than part of the main Git tree.

## v0.14

v0.14 is preserved in `legacy/constitutive_inquiry_mvp_v0_14` as the audited
historical pre-unification baseline. Its confidence-gated relational memory was
safe by complete non-use: the tested memory-use rate was 0%, and behavior was
identical to sparse reset. That result helped motivate the later unified design,
but v0.14 did not generate the paper's final confirmatory results.

The canonical paper implementation is the frozen v0.3 source in `src/`, with
the protocol and manifests in `protocol/` and `manifests/`.

## Use caution

- Do not import the legacy package into the main v0.3 test environment.
- Run legacy tests from an isolated virtual environment and working directory.
- Do not replace v0.3 manifests, outputs, or dependencies with v0.14 files.
- Treat legacy results as historical evidence about development, not as
  confirmatory observations.

