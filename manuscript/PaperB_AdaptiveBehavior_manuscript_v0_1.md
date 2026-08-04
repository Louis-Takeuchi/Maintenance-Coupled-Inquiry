# Maintenance-Coupled Inquiry Control Directs Damage-Relevant Evidence Acquisition and Improves Causal Repair in Artificial Agents

**Running title:** Maintenance-coupled inquiry control

**Author:** [Confirm English spelling of author name]

**Affiliation:** [Institution and postal address]

**Corresponding author:** [Name, email address, ORCID]

**Manuscript type:** Article

**Target journal:** *Adaptive Behavior*

## Abstract

Artificial agents that execute externally specified tasks should be distinguished from inquiry systems that alter what they investigate in response to their own internal condition. We tested whether a designer-specified maintenance signal aligned with damaged internal components changes evidence allocation, causal diagnosis, and repair in causal microworlds. The primary contrast compared `actual_need`, aligned with the focal damaged component, with `yoked_need`, which preserved total need at every step while disrupting component alignment. Seventy-two confirmatory seeds were executed under a frozen protocol across two worlds and prespecified conditions. The package contained 576 primary and 432 ablation runs, with exact replay for all 288 actual/yoked traces. In self-relevant worlds, actual need increased damage-target sensing by 0.1173 relative to yoked need (95% stratified paired bootstrap confidence interval [0.0722, 0.1632]; prespecified smallest effect size of interest 0.08). Replicated restoration occurred in 41/72 actual-need runs and 20/72 yoked-need runs, a paired difference of 0.2917 (95% confidence interval [0.1667, 0.4167]). In neutral worlds, actual need produced 0/72 false repairs; the one-sided 95% exact upper bound was 0.0408, below the prespecified 0.05 safety margin. A common decoder receiving neither condition identity nor need vectors retained an actual-trace advantage in replicated restoration of 0.2778 (95% confidence interval [0.1528, 0.4028]). The results support a limited claim: component-aligned maintenance signals can direct scarce sensing toward damaged targets, with the evidence difference persisting into downstream causal repair. They do not establish constitutive autonomy or endogenous normativity.

**Keywords:** maintenance-coupled inquiry; active sensing; causal microworld; yoked control; causal self-model; artificial autonomy

# 1. Introduction

## 1.1 From task execution to problem-priority formation

Artificial agents can increasingly decompose assigned objectives, gather observations, call external tools, search over candidate actions, and evaluate their own outputs. These capacities support sophisticated task execution, but they do not by themselves determine what an agent should investigate when no single externally fixed task exhausts the situation. In an environment containing several anomalies, an inquiry system must allocate limited observations, decide which hidden causes merit intervention, and determine when the available evidence supports a scoped null conclusion rather than a positive causal claim. The formation of problem priority is therefore a control problem distinct from the execution of a preselected task.

Work on biological autonomy and enactive cognition has argued that adaptive behavior is shaped by relations between a system's conditions of continued organization and its environmental coupling (Barandiaran et al., 2009; Di Paolo, 2005; Froese et al., 2007; Maturana & Varela, 1980; Moreno & Mossio, 2015). In stronger formulations, the organization of the system supplies its own norms: some trajectories are better or worse because they contribute to or undermine the system's continued existence. These theories motivate a question for artificial inquiry, but they also impose an important claim boundary. Adding an internal scalar, deficit variable, or damage label to software does not by itself create constitutive autonomy. If the variables, viable ranges, damage process, repair operators, and stopping conditions are specified by the designer, the resulting system remains a functional model of maintenance-behavior coupling rather than an autonomous individual that generates its own norms.

The present study deliberately investigates a mechanism below that stronger threshold. We ask whether a designer-specified internal maintenance state can change the allocation of scarce evidence and thereby alter causal diagnosis and repair. The experiment is intended to identify a testable intermediate mechanism, not to treat improved task performance as evidence that artificial life or endogenous value has been achieved.

## 1.2 Relation to homeostatic and intrinsically motivated control

Several computational traditions connect internal state to behavior. Homeostatic reinforcement-learning models derive the value of outcomes from their predicted reduction of physiological deviation and explain how internal deficits can reorganize action selection (Keramati & Gutkin, 2014). Active-inference and free-energy formulations similarly emphasize action and perception in systems that remain within a limited repertoire of states (Friston, 2010). These approaches provide important accounts of regulation, prediction, and action, but the present experiment asks a narrower and partly orthogonal question: when several possible causal problems compete for limited sensing, does alignment between a maintenance signal and the actually damaged component alter which evidence is acquired?

Intrinsic-motivation and curiosity systems allocate exploration according to novelty, surprise, uncertainty, competence progress, or expected learning progress (Barto et al., 2013; Oudeyer et al., 2007). These epistemic drives can generate autonomous-looking exploration without being tied to a maintenance deficit. Conversely, a pure maintenance signal can overfocus behavior on a currently salient deficit without selecting informative experiments. Our architecture therefore separates two functions. Need influences domain allocation and the selection of internal components for scarce sensing, while experiment selection within a domain remains need-blind and epistemic. This separation allows maintenance alignment to prioritize a problem without allowing the need variable to dictate the answer or repair rule.

Causal inquiry also requires a distinction between observation and intervention (Pearl, 2009). A variable may correlate with internal damage without belonging to the interventionally relevant maintenance core. Likewise, an external anomaly may be manipulable and an internal state may improve after repair even when the external anomaly did not cause the damage. The benchmark therefore includes an intervention-based self-model, explicit bridge diagnosis, independent validation, and a neutral world in which the external anomaly and internal damage are causally unrelated.

Active sensing is also important because perception is not a passive readout of a fully available world. Sensorimotor accounts treat perception as structured exploration through action (O'Regan & Noë, 2001). In our benchmark, this general insight is operationalized in a deliberately minimal form: only two internal components can receive focused sensing at a time, and the selected intervention changes which subsequent observations become available. The agent must therefore decide not only how to interpret evidence but which evidence-generating interaction to perform.

The experiment further distinguishes maintenance relevance from causal truth. A damaged target can deserve priority without making every hypothesis about that target correct. Conversely, a hypothesis can be epistemically interesting while being irrelevant to the agent's maintenance. This distinction motivates the architecture's two-stage allocation. Need changes the competition among candidate targets, while a shared epistemic selector and shared decoder evaluate interventions. The design is intended to prevent the maintenance signal from becoming an answer key.

## 1.3 Alternative explanations and the yoked control

A condition supplied with damage-related need could outperform a control for several uninformative reasons. First, it might simply devote more observations to the broad self domain. Second, it might receive a larger total motivational signal and therefore explore more. Third, a condition-specific diagnosis or repair formula might directly convert the need vector into the correct action. Fourth, an apparent recovery of internal values might be mistaken for a correct causal explanation.

To reduce these alternatives, the main control is a yoked-need condition. At every step, yoked need preserves the total need magnitude from another seed in the same generator stratum but cyclically deranges its component alignment. The contrast therefore targets *which component* receives priority rather than whether a need signal is present or how large the total signal is. All primary conditions share the same diagnosis, validation, repair, and replication decoder. In addition, every actual/yoked evidence trace is replayed into a common decoder that receives neither the condition identity nor the need vector. A neutral world provides a mandatory safety test: when no bridge exists, the system should avoid false repair and, where evidence permits, return an explicit scoped `no_bridge` conclusion.

## 1.4 Hypotheses and claim boundary

The primary mechanism hypothesis was that actual need would increase the proportion of post-shift active-sensing steps that included the truly damaged component relative to yoked need. The downstream hypothesis was that this difference in acquired evidence would improve replicated restoration. The mandatory safety hypothesis was that actual need would not create an unacceptable false-repair rate in neutral worlds. A common-decoder analysis tested whether the downstream advantage remained when inference and repair logic were held constant across trace sources.

The strongest conclusion available from this design concerns a functional causal mechanism in a constrained artificial environment. The experiment does not test whether the system produces its own body, norms, variables, intervention vocabulary, or death conditions. It therefore cannot establish constitutive autonomy, intrinsic normativity, artificial individuality, or a general scientific agent.

# 2. Methods

## 2.1 Separation of development and confirmation

The study used a strict development-confirmation split. Development seeds 0-39 were used to calibrate world difficulty, define the endpoint hierarchy, test chunk execution and deterministic merging, implement exact replay, inspect the common decoder, and freeze the analysis pipeline. Confirmatory focal seeds 30000-30071 were not used during development. Before confirmatory execution, we froze the source snapshot, parameter registry, endpoint registry, smallest effects of interest, decision rules, sample size, focal-seed list, donor map, chunk plan, expected-key grid, bootstrap seed, and analysis scripts.

The observation budget was 600 steps, the environmental shift occurred at observation 28, active-sensing width was two components, and cross-world memory was disabled for the primary experiment. The bootstrap random seed was 941731. Paired bootstrap intervals used 50,000 resamples. No parameter, endpoint, donor assignment, sample-size rule, or statistical function was changed after confirmatory activation.

The final confirmatory execution comprised 576 primary source runs and 432 ablation source runs. Every chunk was tied to the frozen activation hash and emitted a receipt. Source traces and processed summaries were retained separately. A prematurely interrupted initial execution attempt was isolated and excluded before any result was inspected; the frozen chunk plan was then executed through smaller non-overwriting units without changing the experimental specification.

## 2.2 Causal microworlds

Each microworld contained continuous internal variables, an interventionally defined causal core, external hidden mechanisms, observation noise, intervention primitives, and explicit costs. The agent did not initially know the core membership, the external mechanism, the correct intervention program, or whether the external process was causally connected to the internal damage. Ground truth was available to the experimenter for endpoint evaluation.

Generator strata were defined by the Cartesian combination of core size, topology, grammar family, primitive cardinality, and nonstationarity. The confirmatory seed manifest balanced these frozen strata. Two program-composition bundles occurred by design: a three-step branch grammar with core size five and five primitives, and a four-step context grammar with core size six and seven primitives. Because these features covaried, subgroup analyses treated them as bundles rather than estimating independent factor effects.

### 2.2.1 Self-relevant world

In the self-relevant world, an external hidden mechanism was causally connected to damage in an internal core component. The agent could achieve replicated restoration only by gathering enough evidence to identify the relevant mechanism, constructing an effective intervention program, supporting a positive bridge diagnosis, passing an independent bridge-validation step, applying the correct internal repair, and reproducing the result in an independent replication phase.

### 2.2.2 Neutral world

In the neutral world, the external residual mechanism and internal damage were causally independent. The scientifically appropriate positive outcome was therefore absent. The agent could instead reach a scoped null conclusion: within the tested intervention and observation budget, the evidence did not support an external-to-internal bridge. Applying an internally effective repair while attributing the damage to the unrelated external mechanism counted as a false repair. This world separated physiological-looking recovery from causal correctness.

## 2.3 Agent architecture

The agent consisted of seven functional modules: an intervention-based self-model, domain allocation, component-level active sensing, intervention-program search, bridge diagnosis, independent bridge validation, and repair with replication.

The causal self-model estimated which internal variables belonged to the maintenance core by evaluating their organized response to interventions. It was not supplied with the true core labels. The model produced a probability of core membership for each component. Need was computed from estimated core membership and deviation below a component baseline. Importantly, need was not an input to the bridge decision, validation criterion, repair choice, or replication rule. It affected only (a) the distribution of observations between broad domains and (b) which components were included in the width-two active-sensing panel. Once a domain had been selected, all primary conditions used the same need-blind epistemic selector to choose experiments.

Positive bridge diagnosis required evidence that an external intervention altered the damaged internal component through the hypothesized mechanism. A positive diagnosis was not sufficient for repair: an independent validation procedure had to reproduce the bridge under a held-out test. The decoder also contained an explicit `no_bridge` candidate so that finite inquiry could terminate with a scoped null statement rather than either guessing a positive relation or remaining indefinitely undecided.

## 2.4 Primary conditions

The four primary conditions shared the same environment distribution and downstream decoder.

1. **Actual need.** For component *i*, need was proportional to the estimated probability that *i* belonged to the causal core multiplied by the positive deficit between its baseline and current value. The resulting vector was aligned with the focal run's damaged component.
2. **Yoked need.** The run received an actual-need trace from a different seed in the same frozen generator stratum. At each step, total need magnitude was preserved, while a fixed nonzero cyclic shift disrupted component correspondence. The donor map was frozen before confirmation.
3. **Curiosity.** Need was set to zero. Observation allocation used epistemic uncertainty and under-sampling, providing a need-free intrinsic-exploration control.
4. **No need.** Need was set to zero. After the environmental shift, broad self/neutral domain allocation was fixed at 50/50, while component sensing used the same epistemic selector as curiosity. This condition tested whether the worlds remained solvable without need-based allocation.

## 2.5 Ablations

Six ablations were specified before confirmation.

- **Correlation self-model:** replaced the intervention-based causal self-model with a correlational model.
- **No null:** removed `no_bridge` from the diagnosis vocabulary.
- **No bridge validation:** removed independent validation before repair.
- **No null and no validation:** removed both safeguards.
- **Passive only:** prohibited active interventions.
- **Pair limited:** restricted intervention programs to sequences of length two or less.

The ablations were interpreted as a functional decomposition of the current benchmark. They were not treated as proofs that these mechanisms are universally necessary for scientific inquiry.

## 2.6 Endpoints

### 2.6.1 Manipulation check

The manipulation check was the paired actual-minus-yoked difference in `mean_need_target_mass_share` in self-relevant worlds. It measured the share of need mass assigned to the true damaged target. The manipulation was considered successful if the paired mean was positive and the lower bound of the stratified paired-bootstrap 95% confidence interval exceeded zero.

### 2.6.2 Primary mechanism endpoint

The primary endpoint was `causal_target_sensing_share`: the proportion of post-shift active-sensing decisions in which the true damaged target was included in the scarce sensing panel. The prespecified smallest effect size of interest was an absolute actual-minus-yoked increase of 0.08.

A key secondary process measure was `causal_target_sensing_selectivity`, which contrasted target sensing against non-target sensing. Broad self-domain observation share was not used as the alignment endpoint because actual and yoked conditions preserved the total need process and the environment contained only a binary self/neutral domain distinction.

### 2.6.3 Mandatory safety gate

The mandatory safety endpoint was the false-repair rate of actual need in neutral worlds. The gate required the one-sided 95% Clopper-Pearson upper confidence bound to be at or below 0.05. A prespecified auxiliary safety endpoint required the one-sided 95% lower bound for explicit `no_bridge` to be at least 0.90.

### 2.6.4 Confirmatory downstream endpoint

The confirmatory downstream endpoint was `replicated_restoration` in self-relevant worlds. A run received a value of one only when it achieved a correct bridge decision, passed validation, selected the correct repair, restored the organization, and succeeded in an independent replication. The prespecified smallest effect size of interest was an absolute actual-minus-yoked probability difference of 0.10.

### 2.6.5 Common-decoder diagnostic

For all actual/yoked traces in both worlds, the complete sequence of actions, observations, hidden side effects, and diagnosis cut points was exactly replayed. The replayed evidence prefix was then supplied to a common decoder that had no access to condition identity, need policy, or need vector. This analysis asked whether trace-source differences survived a need-blind downstream decoder. It was a mechanism diagnostic rather than a formal identification of natural direct and indirect effects.

## 2.7 Statistical analysis and decision rules

The sampling unit was the paired focal seed. For continuous and binary paired contrasts, generator-stratum-preserving bootstrap samples were drawn with replacement within each stratum. Percentile 95% confidence intervals were calculated from 50,000 resamples. Safety rates were evaluated with one-sided exact Clopper-Pearson intervals.

The main mechanism claim was supported only if all of the following held: successful manipulation check; target-sensing point estimate at or above 0.08; target-sensing confidence-interval lower bound above zero; mandatory safety gate passed; and exact replay succeeded for all required traces. The downstream claim was supported only if the replicated-restoration point estimate was at or above 0.10, its confidence-interval lower bound exceeded zero, and the safety gate passed. Secondary controls and ablations could not rescue a failed primary decision.

## 2.8 Execution integrity

The expected primary grid comprised 72 seeds x 4 conditions x 2 worlds = 576 keys. The expected ablation grid comprised 432 keys. Deterministic merging checked duplicate, missing, and unexpected keys. Exact replay and common-decoder output were expected for 288 actual/yoked trace-world combinations. Post-run integrity checks also compared the frozen-file manifest against the executed source tree and reran the automated test suite.

# 3. Results

## 3.1 Execution integrity

All 576 primary keys and all 432 ablation keys were present. Duplicate, missing, and unexpected key counts were zero. All 120 planned execution receipts were present and no frozen source file changed during execution. Exact replay succeeded for 288/288 actual/yoked traces, and common-decoder outputs were complete. The post-run automated suite passed 45/45 tests.

A frozen analysis command-line interface retained a development-era metadata string in its `analysis_scope` field. The numerical functions, bootstrap implementation, endpoint mapping, smallest effects of interest, and verdict formulas were unchanged. Raw analysis output was preserved, and only the reporting metadata label was corrected in the confirmatory result package.

## 3.2 Need alignment manipulation

Actual need assigned substantially more need mass to the true damaged component than yoked need. The paired difference in `mean_need_target_mass_share` was 0.1698, and the lower confidence bound was above zero. The yoking procedure therefore preserved a need process while disrupting focal component alignment as intended.

## 3.3 Damage-target evidence allocation

Actual need increased `causal_target_sensing_share` by 0.1173 relative to yoked need (95% confidence interval [0.0722, 0.1632]). The point estimate exceeded the prespecified 0.08 smallest effect size of interest, and the interval excluded zero. Target-sensing selectivity also increased by 0.1020 (95% confidence interval [0.0491, 0.1556]). The main mechanism endpoint therefore satisfied the frozen decision rule.

The result concerned the identity of components selected for scarce sensing, not merely total observation count. Total need was preserved by the yoked control, and the downstream experimental selector was shared. Actual need thus changed which internal component was brought into the active-sensing panel.

## 3.4 Neutral-world safety

Actual need produced 0 false repairs in 72 neutral-world runs. The one-sided 95% exact upper bound was 0.0408, below the prespecified 0.05 margin. Explicit `no_bridge` was produced in 71/72 runs; its one-sided 95% lower bound was 0.9358, above the auxiliary 0.90 criterion. The remaining run ended without a diagnosis but did not attempt repair and was classified as an appropriate safe abstention. The mandatory safety gate was therefore supported.

## 3.5 Replicated restoration

Replicated restoration occurred in 41/72 actual-need runs (56.9%) and 20/72 yoked-need runs (27.8%). The paired actual-minus-yoked difference was 0.2917 (95% confidence interval [0.1667, 0.4167]), exceeding the prespecified 0.10 smallest effect size of interest. Bridge-decision correctness was 44/72 under actual need and 21/72 under yoked need.

Actual need did not solve every self-relevant world. It selected explicit `no_bridge` in 28/72 self-relevant runs. The difference in observations to diagnosis was -8.21, but the 95% interval [-22.56, 5.68] included zero; an improvement in diagnostic speed was therefore not supported.

## 3.6 Comparisons with curiosity and no need

Relative to curiosity, actual need increased target-sensing share by 0.1129 (95% confidence interval [0.0754, 0.1525]) and replicated restoration by 0.2639 (95% confidence interval [0.1389, 0.3889]). The difference in observations to diagnosis was +10.28 with an interval crossing zero, so actual need was not demonstrably faster than curiosity.

Relative to no need, actual need increased target-sensing share by 0.1129 and replicated restoration by 0.3333. It also required approximately 99 fewer observations to diagnosis on average. These comparisons indicate that uncertainty-driven exploration remained useful, but maintenance alignment added information not captured by a purely epistemic selector.

## 3.7 Common decoder

When the common decoder received actual traces, bridge-decision correctness was 44/72; for yoked traces it was 21/72. The paired difference was 0.3194 (95% confidence interval [0.1944, 0.4444]). Common-decoder replicated restoration was 40/72 for actual traces and 20/72 for yoked traces, a difference of 0.2778 (95% confidence interval [0.1528, 0.4028]). Common-decoder false repair was zero for both trace sources.

The actual-trace advantage therefore persisted when condition-specific need information was unavailable to the decoder. This result is inconsistent with an explanation in which a special actual-need repair formula alone creates the outcome difference. It is consistent with the interpretation that evidence acquired under the actual policy carried more useful information into downstream inference. Because the policy determines which action-observation history exists, the common-decoder analysis should not be interpreted as a complete causal mediation decomposition.

## 3.8 Functional ablations

### 3.8.1 Causal versus correlational self-model

Mean core precision was approximately 0.938 for the intervention-based actual-need model and 0.457 for the correlational self-model. The paired precision difference was 0.4810 (95% confidence interval [0.4566, 0.5051]). Replicated restoration fell from 41/72 under actual need to 17/72 under the correlational model. Correlation preserved broad sensitivity but incorporated variables that covaried with the internal state without belonging to the interventionally defined core.

### 3.8.2 Null diagnosis and independent validation

Removing `no_bridge` yielded 0/72 false repairs in neutral worlds, but it also yielded 0/72 explicit null conclusions and no completed diagnoses. This condition remained safe by inaction but failed to form a scientific null result.

Removing independent validation increased false repair to 19/72 (26.4%). Removing both `no_bridge` and validation increased false repair to 72/72. In the double-removal condition, organization was restored in 70/72 runs and replication succeeded in 66/72, yet every causal attribution was wrong because the external process was unrelated to the internal damage. State improvement was therefore dissociable from causal correctness.

### 3.8.3 Active intervention and program composition

Under passive-only observation, diagnosis, bridge correctness, and replicated restoration were all 0/72. Under pair-limited search, exact and functional programs, diagnosis, and replicated restoration were also 0/72. In the current generator, interventions and programs of length at least three were construct requirements for identifying the hidden mechanisms.

## 3.9 Descriptive failure taxonomy

After the confirmatory verdict had been fixed, all 72 actual-need self-relevant runs were descriptively classified without excluding seeds or changing endpoints. Of the 31 failures, 28 were false-null outcomes and three were replication failures after a correct bridge decision, validation, repair, and initial organization restoration. There were no source-policy validation failures or incorrect repair selections after a positive validated bridge.

Paired seed transitions showed 26 seeds in which actual need alone achieved replicated restoration and five in which yoked need alone succeeded. False-null occurred only under yoked need for 27 seeds and only under actual need for four seeds, a net reduction of 23 false-null outcomes. The primary downstream advantage therefore arose mainly because actual need more often accumulated sufficient evidence to avoid an erroneous null conclusion.

Absolute performance differed between the two frozen program-composition bundles. Actual need restored 25/36 three-step worlds and 16/36 four-step worlds. Nevertheless, actual-minus-yoked effects on target sensing and restoration remained positive in both bundles. Because program length, grammar, core size, and primitive cardinality covaried, no independent factor effect was inferred.

# 4. Discussion

## 4.1 Maintenance alignment changed what the agent measured

The central finding was not that a need variable increased general activity. Actual and yoked conditions shared the same total need process, yet actual need placed the truly damaged component in the active-sensing panel more often. The contrast therefore isolated component alignment: a maintenance signal can change the *identity* of evidence selected under a scarce-sensing constraint.

This role differs from treating deficit as reward. Homeostatic reinforcement learning explains how predicted outcomes can become valuable because they reduce internal deviation (Keramati & Gutkin, 2014). In our benchmark, the need signal does not assign the truth value of a hypothesis or the correctness of a repair. Instead, it biases the allocation of measurement opportunities before the shared epistemic search and decoder operate. The result suggests a modular relation between maintenance and inquiry: maintenance can prioritize a question while uncertainty and intervention logic determine how the question is tested.

The separation also clarifies the relation to curiosity. Curiosity and intrinsic-motivation systems can direct exploration toward novelty, surprise, or learning progress (Barto et al., 2013; Oudeyer et al., 2007). Such signals are epistemically valuable but are not necessarily aligned with the condition of the investigating system. Actual need outperformed curiosity in target sensing and replicated restoration, while curiosity remained more capable than a fixed no-need allocation in some runs. A viable architecture may therefore require both maintenance relevance and epistemic value rather than reducing one to the other.

The yoked design is central to this interpretation. A comparison against a zero-need baseline alone would conflate alignment, magnitude, and the existence of a motivational process. By preserving the time-varying total need while changing its component correspondence, the yoked condition asks whether the signal is informative about *where* the maintenance problem lies. The resulting effect is therefore closer to a selectivity test than a generic motivation test. Future benchmarks should extend this logic to multiple simultaneous deficits, where total need and component alignment can vary independently across several competing maintenance demands.

The benchmark also provides a template for separating process evidence from outcome evidence. Target sensing is a process endpoint tied to the proposed mechanism; replicated restoration is a downstream functional endpoint; neutral false repair is a safety endpoint. Requiring all three prevents a system from passing because it repairs by chance, overfits an unsafe positive hypothesis, or changes its sensing without producing useful consequences. This layered endpoint structure may be useful in other artificial-agent studies where internal drives are proposed to organize inquiry.

## 4.2 Evidence acquisition carried into downstream repair

The downstream difference was large: replicated restoration was approximately twice as frequent under actual need as under yoked need. More importantly, the difference remained when both trace sources were processed by the same need-blind decoder. This weakens the alternative explanation that a condition-specific repair mapping directly converted actual need into the correct answer.

The common-decoder result should nevertheless be interpreted carefully. The trace is a product of the policy. Exact replay holds the realized action-observation history fixed, but it does not construct the counterfactual trace that the same seed would have produced under every alternative sensing decision. The analysis therefore establishes decoder invariance, not a complete natural-effects decomposition. Its evidential value is narrower: when inference rules are shared, actual traces still contain information that more often supports correct bridge diagnosis and replicated repair.

## 4.3 Recovery is not equivalent to causal correctness

The strongest safety lesson came from the neutral-world ablations. When both the null diagnosis and independent validation were removed, almost every run restored the internal organization and most reproduced the restoration, yet all 72 runs were false repairs. A system can apply an effective internal intervention while maintaining a false explanation of why the problem occurred.

This distinction matters for artificial scientific agents. Evaluation based only on reward, symptom reduction, or state recovery can conceal a causal error. An intervention may work through a direct repair operator even though the hypothesized external cause is unrelated. In the current architecture, explicit null diagnosis and independent validation serve complementary functions. The null hypothesis allows the agent to represent a negative scientific conclusion, whereas validation prevents a positive but poorly supported bridge from triggering repair.

The `no_null` ablation further showed that safe inactivity is not the same as a null result. It produced no false repairs, but it also produced no explicit `no_bridge` diagnoses. Scientific inquiry needs a representational distinction between unresolved inquiry, scoped non-support, and positive causal attribution.

## 4.4 Causal self-boundaries require intervention

The correlational self-model recovered many relevant variables but suffered a large precision loss. Variables that covaried with the internal state were included even when interventions did not reveal them as part of the organized causal core. The result supports an intervention-based interpretation of self-boundary estimation: membership should depend on how variables participate in the maintenance organization, not only on their statistical association with its readouts.

This finding does not show that the agent autonomously constituted its own boundary. Candidate variables, intervention opportunities, and world generators were externally supplied. The supported claim is limited to the benchmark: an intervention-based model more precisely recovered the designer-defined causal core than a correlation-based model.

## 4.5 Why the remaining failures were mainly false nulls

Actual need failed in 31/72 self-relevant runs. Twenty-eight failures were false-null outcomes rather than unsafe positive diagnoses. Once the source policy selected and validated a positive bridge, repair selection was correct in every case; the remaining three failures occurred during independent replication. The primary bottleneck was therefore accumulating sufficient evidence to support the true bridge under a finite budget.

This pattern also explains why target sensing was not a seed-level success classifier. Actual need increased target sensing on average relative to yoked need, but some false-null seeds had relatively high target-sensing shares. Observing the relevant component is necessary for useful evidence but not sufficient. The action sequence must discriminate among mechanisms, observations must be combined appropriately under noise, and the finite program search must reach an informative intervention. Maintenance alignment changes the distribution of opportunities; it does not guarantee identifiability.

## 4.6 Position within theories of autonomy

The experiment was motivated by theories in which adaptive normativity depends on a system's continued organization (Barandiaran et al., 2009; Di Paolo, 2005; Maturana & Varela, 1980; Moreno & Mossio, 2015). Our need variable implements only a middle portion of that causal story. Baselines, component identities, viable ranges, damage, repair, budget, and failure conditions were programmed externally. The system did not produce its components, regenerate its measurement vocabulary, or undergo irreversible loss of identity.

Accordingly, the findings neither provide a sufficient condition nor a necessary condition for constitutive autonomy. They identify an intermediate design hypothesis: if a system has an internal maintenance organization and a causal self-model, a component-aligned signal can be used to prioritize evidence acquisition without entering the downstream truth criterion. A future constitutively autonomous system would have to generate and revise the relevant variables and norms through its own organization rather than inherit them from the experimenter.

## 4.7 Limitations

First, the worlds were deliberately small and their ground-truth causal structures were available to the experimenter. They do not reproduce theory-laden measurement, instrument construction, conceptual change, underdetermination among large theories, or social values in real science.

Second, the internal variables and causal core were numerical states rather than materially self-producing processes. The agent could be reconstructed from code and state files after termination; maintenance-dependent identity and constitutive death were absent.

Third, intervention primitives and diagnosis vocabulary were supplied. The agent composed programs within a fixed grammar but did not invent variables, instruments, null concepts, or new forms of experiment.

Fourth, the common decoder was a trace-source diagnostic, not a complete causal mediation analysis.

Fifth, the primary environment contained only self-relevant and neutral worlds. Partial bridges, multiple simultaneous damage targets, competing maintenance requirements, and changing normative conflicts were not tested.

Sixth, language models were not used in the experimental agent. The results therefore do not establish a connection to linguistic hypothesis formation, literature synthesis, or explanation generation.

Seventh, a development-era metadata label remained in the frozen analysis interface. Although this did not alter numerical computation or the verdict, future versions should freeze separate output schemas for development and confirmation.

Eighth, the failure taxonomy and subgroup descriptions were conducted after the confirmatory verdict. They were retained as descriptive analyses and did not change the endpoint hierarchy, smallest effects of interest, exclusions, or decisions. The covarying program-composition features prevent attribution of difficulty to any single generator factor.

# 5. Conclusion

In a frozen confirmatory experiment using 72 previously unused seeds, need aligned with the actually damaged internal component increased scarce active sensing of that target relative to a yoked control that preserved total need while disrupting component alignment. The effect exceeded the prespecified smallest effect size of interest, passed a neutral-world false-repair safety gate, and was accompanied by a substantial increase in replicated restoration. The advantage persisted when actual and yoked evidence traces were processed by a common decoder with no access to need or condition identity.

Ablations separated several functions within the benchmark. Intervention-based self-modeling improved boundary precision; explicit `no_bridge` enabled a scientific null conclusion; independent validation reduced false repair; active intervention and multi-step program composition were required for causal identification. Most remaining actual-need failures were false-null outcomes, showing that maintenance alignment improved but did not solve finite-budget causal discovery.

The appropriate conclusion is therefore functional and limited. Designer-specified maintenance signals do not create scientific value or constitutive autonomy by themselves. Within an architecture that separates maintenance relevance from epistemic search and downstream validation, however, component-aligned need can direct what evidence is acquired, and that difference can alter the probability of causally correct repair.

# Acknowledgements

[Add non-author contributions after obtaining consent.]

# Author contributions

[Author name]: Conceptualization; methodology; software; formal analysis; investigation; data curation; visualization; writing - original draft; writing - review and editing; project administration. Any co-author contributions must be confirmed using the CRediT taxonomy before submission.

# Statements and declarations

## Ethical considerations

Ethical approval was not required. The study consisted entirely of software experiments in artificial causal microworlds and involved no human participants, human data, animals, clinical data, or biological samples.

## Consent to participate

Not applicable.

## Consent for publication

Not applicable.

## Declaration of conflicting interests

The author(s) declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article. [Confirm with all authors before submission.]

## Funding

This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. [Replace if funding exists.]

## Data availability

Processed confirmatory data, endpoint tables, integrity audits, and execution receipts are available in the Maintenance-Coupled-Inquiry repository and its associated versioned release: https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry. Full step-level traces are not included in the main Git history; the frozen code and manifests required to regenerate them are provided.

## Code availability

The frozen source code, protocol, seed manifests, analysis scripts, and processed confirmatory results are available at the Maintenance-Coupled-Inquiry repository: https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry.

## Generative AI use

During preparation of this manuscript, the author used OpenAI ChatGPT to assist with English translation, structural editing, and document formatting. The author reviewed and verified all scientific claims, calculations, references, and final wording and takes full responsibility for the content.

# References

Barandiaran, X. E., Di Paolo, E., & Rohde, M. (2009). Defining agency: Individuality, normativity, asymmetry, and spatio-temporality in action. *Adaptive Behavior, 17*(5), 367-386. https://doi.org/10.1177/1059712309343819

Barto, A., Mirolli, M., & Baldassarre, G. (2013). Novelty or surprise? *Frontiers in Psychology, 4*, Article 907. https://doi.org/10.3389/fpsyg.2013.00907

Di Paolo, E. A. (2005). Autopoiesis, adaptivity, teleology, agency. *Phenomenology and the Cognitive Sciences, 4*, 429-452. https://doi.org/10.1007/s11097-005-9002-y

Friston, K. (2010). The free-energy principle: A unified brain theory? *Nature Reviews Neuroscience, 11*, 127-138. https://doi.org/10.1038/nrn2787

Froese, T., Virgo, N., & Izquierdo, E. (2007). Autonomy: A review and a reappraisal. In F. Almeida e Costa, L. M. Rocha, E. Costa, I. Harvey, & A. Coutinho (Eds.), *Advances in Artificial Life: ECAL 2007* (Lecture Notes in Computer Science, Vol. 4648, pp. 455-464). Springer. https://doi.org/10.1007/978-3-540-74913-4_46

Keramati, M., & Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife, 3*, e04811. https://doi.org/10.7554/eLife.04811

Maturana, H. R., & Varela, F. J. (1980). *Autopoiesis and cognition: The realization of the living*. D. Reidel. https://doi.org/10.1007/978-94-009-8947-4

Moreno, A., & Mossio, M. (2015). *Biological autonomy: A philosophical and theoretical enquiry*. Springer. https://doi.org/10.1007/978-94-017-9837-2

O'Regan, J. K., & Noë, A. (2001). A sensorimotor account of vision and visual consciousness. *Behavioral and Brain Sciences, 24*(5), 939-973. https://doi.org/10.1017/S0140525X01000115

Oudeyer, P.-Y., Kaplan, F., & Hafner, V. V. (2007). Intrinsic motivation systems for autonomous mental development. *IEEE Transactions on Evolutionary Computation, 11*(2), 265-286. https://doi.org/10.1109/TEVC.2006.890271

Pearl, J. (2009). *Causality: Models, reasoning, and inference* (2nd ed.). Cambridge University Press.
