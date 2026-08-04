# v0.15 Plan — Non-Vacuous Transfer and Calibrated Applicability

## Motivation

v0.14 eliminated the negative transfer seen in v0.13, but did so by rejecting every transferred-memory proposal. The principal condition was exactly identical to matched sparse local search. Safety was achieved through non-use, not through reliable memory.

The next version must make memory use both **evaluable** and **accountable**.

## Central question

Can cross-world memory change inquiry in a controlled subset of worlds and improve search relative to matched sparse local search, without reducing recovery or increasing neutral-world intervention?

## Design requirements

1. **Hidden applicability variable**
   - construct worlds in which prior memory is applicable, partially applicable, or structurally incompatible;
   - keep this status hidden from the agent;
   - report calibration separately for each stratum.

2. **Calibrated action gate**
   - treat mapping trust as a probability-like forecast rather than an arbitrary threshold score;
   - report Brier score, expected calibration error, coverage, and conditional accuracy;
   - freeze the gate on development worlds before confirmation.

3. **Non-vacuous coverage requirement**
   - require transferred memory to change action in a pre-registered minimum fraction of self-relevant worlds;
   - a system that rejects every proposal automatically fails the transfer claim, regardless of recovery.

4. **Matched local counterfactual**
   - preserve the best local branch whenever memory acts;
   - compare memory and local prefixes under matched evidence and cost;
   - record the marginal sequence savings caused by memory content.

5. **Bounded influence**
   - memory may reorder or replace only a fixed fraction of the beam;
   - it cannot remove all local candidates before current-world superiority is demonstrated;
   - search-stage stalls count as negative evidence immediately.

6. **Adversarial proposals that cross the gate**
   - construct wrong memories with initial support comparable to correct memories;
   - require detection or neutralization before repair or irreversible loss of the local branch.

7. **Change-point detection**
   - test for relation-law changes with held-out pair residuals;
   - suspend or down-weight memory after detected nonstationarity;
   - distinguish correct abstention from a permanently closed gate.

8. **Memory-value decomposition**
   - compare full reset, sparse reset, calibrated gate without memory content, correct memory, shuffled memory, and oracle;
   - attribute savings separately to calibration policy, memory proposal quality, and stopping policy.

## Primary conditions

- calibrated non-vacuous memory;
- matched sparse reset;
- identical gate with memory content removed;
- memory without protected local counterfactual;
- memory without change-point detection;
- adversarial memory calibrated to cross the gate;
- ungated memory;
- oracle;
- forced-positive null ablation.

## Pre-registered success criteria

A beneficial-transfer claim requires all of the following:

- restoration difference versus sparse reset at least −0.05;
- at least 5% fewer evaluated sequences than sparse reset;
- memory changes action in at least 25% of self-relevant worlds;
- among action-changing cases, at least 70% of changes reduce search or improve diagnosis time without harming restoration;
- neutral false-repair point estimate below 5%, with uncertainty reported;
- at least 80% of adversarial action-changing memories are detected or neutralized before repair;
- nonstationary restoration no more than 10 percentage points below stationary restoration.

Failing the coverage criterion is classified as **vacuous safety**, not successful transfer.

## Scope

v0.15 remains a stipulated simulation. It improves the epistemic evaluation of memory-guided inquiry; it does not implement constitutive death, physical precariousness, or endogenous normativity.
