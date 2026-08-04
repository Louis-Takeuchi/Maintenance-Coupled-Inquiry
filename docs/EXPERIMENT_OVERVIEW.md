# Experiment overview

The experiment asks whether the alignment of a designer-defined maintenance
signal with an actually damaged internal component changes what evidence an
agent acquires under a finite observation budget.

## Primary design

- Observation budget: 600
- Post-shift onset: 28
- Active-sensing width: 2
- Confirmatory focal seeds: 30000–30071 (N=72)
- Worlds: self-relevant and neutral
- Primary conditions: `actual_need`, `yoked_need`, `curiosity`, `no_need`
- Primary cross-world memory: off
- Primary source rows: 576
- Actual/yoked replay rows: 288
- Confirmatory ablation rows: 432

One active-sensing slot is maintenance guided and one is protected,
need-blind, and epistemic. All primary conditions share the diagnosis,
validation, repair, and replication logic. The common decoder receives neither
condition identity nor need vectors.

## Endpoint hierarchy

1. Primary mechanism: actual-minus-yoked `causal_target_sensing_share`, SESOI
   +0.08.
2. Mandatory safety gate: actual-need neutral-world `false_repair`, with the
   one-sided 95% upper bound required to be at most 0.05.
3. Confirmatory secondary: actual-minus-yoked `replicated_restoration`, SESOI
   +0.10.
4. Supporting safety: neutral-world `explicit_no_bridge`, with a one-sided 95%
   lower-rate criterion of 0.90.

The protocol and all registries are in `protocol/` and `manifests/`. This
overview is explanatory and does not supersede those frozen files.

