# Supplementary Materials

## Maintenance-Coupled Inquiry Control Directs Damage-Relevant Evidence Acquisition and Improves Causal Repair in Artificial Agents

**Protocol:** Frozen confirmatory protocol v0.3  
**Confirmatory focal seeds:** 30000-30071  
**Analytic status:** Descriptive supplementary decomposition performed after the confirmatory verdict. No primary endpoint, smallest effect size of interest, decision rule, exclusion rule, or seed set was changed.

# S1. Purpose and claim boundary

The main experiment showed that actual need increased damage-target sensing and replicated restoration relative to yoked need, but the absolute replicated-restoration rate under actual need was 41/72. The supplementary analysis retains all 72 focal seeds and decomposes the remaining failures by processing stage. It also describes within-seed actual-yoked transitions, performance across frozen generator bundles, the relation between target sensing and individual outcomes, common-decoder stage counts, and the single neutral-world run that did not produce an explicit null diagnosis.

These analyses do not introduce new confirmatory claims. They are not used to redefine or rescue the main effect, and they do not identify independent causal effects of the generator factors that covaried by design.

# S2. Supplementary methods

## S2.1 Data

The analysis used the 576-run primary confirmatory dataset. Self-relevant actual need, yoked need, curiosity, and no need each contributed 72 runs. The neutral safety exception analysis used 72 neutral actual-need runs. Common-decoder summaries used 72 actual and 72 yoked traces. No seed was excluded.

## S2.2 Exclusive failure taxonomy

Each self-relevant actual-need seed was assigned to one exclusive outcome category.

1. **Replicated restoration success:** `replicated_restoration = 1`.
2. **False null with mechanism identity retained:** `false_null = 1` and `mechanism_correct = 1`. The external mechanism was identified, but the bridge to self-damage was rejected.
3. **False null with mechanism not identified:** `false_null = 1` and `mechanism_correct = 0`.
4. **Replication failure after correct repair:** bridge decision, validation, repair, and organization restoration succeeded, but independent replication failed.
5. **Other failure:** no diagnosis, validation failure, or repair failure. No actual-need confirmatory run entered this residual category.

In a self-relevant world, `false_null` denotes an explicit `no_bridge` decision despite a true bridge. In a neutral world, `no_bridge` is an appropriate scientific null conclusion and is not a failure.

## S2.3 Paired transitions

Actual and yoked runs were matched by focal seed. Binary outcomes for replicated restoration, bridge-decision correctness, and false null were displayed as 2 x 2 transition tables. These tables decompose the already reported paired mean differences into concordant and discordant seed counts; they are not new significance tests.

## S2.4 Frozen strata and program-composition bundles

Frozen generator strata were defined by `core_size x grammar_family x primitive_cardinality x nonstationary x topology`. For compact description, two covarying bundles were also reported:

- three-step branch composition, core size five, five primitives;
- four-step context composition, core size six, seven primitives.

Because these features changed together, performance differences cannot be assigned independently to program length, grammar, core size, or primitive cardinality.

## S2.5 Target sensing and individual success

The primary target-sensing endpoint was defined as a paired causal contrast between actual and yoked policies, not as a seed-level classifier. Target-sensing distributions were therefore summarized by failure category and difficulty bundle without fitting a post hoc success threshold.

# S3. Supplementary results

## S3.1 Actual-need failures were concentrated in false-null outcomes

Replicated restoration occurred in 41/72 actual-need runs. The remaining 31 runs consisted of 12 false-null outcomes with external-mechanism identity retained, 16 false-null outcomes without correct mechanism identity, and three replication failures after correct repair. Validation failure and source-policy repair failure were both 0/72.

All 44 runs that adopted a positive bridge passed validation, selected the correct repair, and restored the organization. Forty-one of these also passed independent replication. Thus, the main residual bottleneck was not unsafe positive diagnosis or incorrect repair after validation. It was failure to accumulate enough evidence for the true bridge before the finite budget ended.

## S3.2 The actual-yoked difference appeared mainly as reduced false nulls

For replicated restoration, 26 seeds succeeded only under actual need, five succeeded only under yoked need, 15 succeeded under both, and 26 failed under both. The net discordance of 21 seeds corresponds to the observed 41/72 versus 20/72 rates.

False null occurred only under yoked need in 27 seeds and only under actual need in four seeds; 24 seeds were false-null under both policies and 17 under neither. Actual need therefore reduced false-null outcomes by a net 23 seeds. Bridge-decision correctness showed the same 27-versus-four discordance. The downstream actual advantage was consequently expressed mainly through avoidance of erroneous null decisions.

## S3.3 Absolute performance differed across the covarying difficulty bundles

In the three-step bundle, actual need achieved replicated restoration in 25/36 runs (69.4%) and false null in 8/36 runs (22.2%). In the four-step bundle, replicated restoration was 16/36 (44.4%) and false null was 20/36 (55.6%).

The actual-minus-yoked target-sensing difference remained positive in both bundles: +0.1484 in the three-step bundle and +0.0863 in the four-step bundle. Replicated-restoration differences were also positive in both: +0.2500 and +0.3333, respectively. The main effect direction therefore did not depend exclusively on one bundle, although absolute performance was lower in the larger four-step bundle.

## S3.4 More target sensing was not sufficient for seed-level success

Across all actual-need runs, mean target-sensing share was 0.2421 in the false-null group and 0.2283 in the replicated-restoration group. Within the three-step bundle, the corresponding values were 0.3274 and 0.2269; within the four-step bundle, 0.2080 and 0.2304.

There was therefore no simple monotonic seed-level relation in which more target sensing guaranteed success. The primary result is an average causal comparison: actual need changed the distribution of sensing relative to yoked need. Individual success remained constrained by intervention-sequence identifiability, noise, evidence combinations, and the finite search budget.

## S3.5 The common decoder introduced one additional repair-stage loss

The common decoder produced a diagnosis for all 72 actual traces. It achieved 44 correct bridge decisions, 43 correct repairs, and 40 replicated restorations. For yoked traces, it achieved 21 correct bridge decisions, 21 correct repairs, and 20 replicated restorations.

The source policy selected the correct repair in all 44 actual runs with a positive validated bridge, whereas the common decoder lost one run at the repair stage. Replication failed after organization restoration in three actual traces and one yoked trace. The actual advantage remained, but a common reconstruction of the decoder did not reproduce every source-policy decision exactly.

## S3.6 The single neutral exception was safe indecision

Actual need produced zero false repairs in 72 neutral runs and returned explicit `no_bridge` in 71. Seed 30016 reached the observation budget without a completed diagnosis. It did not attempt repair and was coded as an appropriate abstention and a correct safe decision, but not as a scientific null result.

This exception distinguishes explicit scoped non-support from safe indecision. The system was not perfectly complete in producing null statements, although the exception did not create an unsafe positive action.

# S4. Interpretation

The supplementary decomposition indicates that maintenance-aligned inquiry improved downstream performance primarily by reducing false-null outcomes that were more common under yoked need. Once the source policy selected and validated a positive bridge, repair accuracy was effectively saturated. The remaining challenge was finite-budget causal identification.

The analysis also sharpens the claim boundary. Maintenance alignment increased average evidence allocation and restoration probability, but it was not a complete causal-discovery solution. Performance was lower in the larger program-composition bundle, and target-sensing quantity alone did not predict individual success. The findings continue to support a functional mechanism rather than constitutive autonomy or endogenous normativity.

# S5. Reproducibility

The supplementary tables and figures were generated from `PaperB_confirmatory_primary_run_summaries_v0_3.csv` and `PaperB_confirmatory_ablation_run_summaries_v0_3.csv`. The package includes seed-level taxonomy, stage counts, paired transitions, frozen-stratum descriptions, the neutral exception, and common-decoder stage counts. The frozen confirmatory source and verdict files were not modified.
