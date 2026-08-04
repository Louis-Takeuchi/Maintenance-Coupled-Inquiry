# 論文B 統一確認実験プロトコル候補 v0.3

**日付:** 2026-08-04  
**状態:** pre-confirmatory freeze candidate / confirmatory episode未実行  
**対象:** 維持結合型探究制御の機能モデル

## 1. 中心的な問い

> 設計された内部維持状態に成分対応したneedは、総need量を保ちながら成分対応を崩したyoked needと比べ、限られた能動センシングを実際の損傷対象へ配分し、その証拠差を通じて因果診断と修復を改善するか。

本実験は構成的自律性、内生的規範、構成的な死、一般的な科学者AIを検証しない。内部変数、正常域、損傷、修復、行動費用、世界生成器、介入語彙は設計者が与える。

## 2. v0.2からの変更理由

Development ablationにより、`organization_restored`単独では因果的に正しいrepairを保証しないことが確認された。誤った外部原因を選んでもrestore operatorが内部値を改善できるためである。また`no_bridge`単独除去ではfalse repairが起きない一方、neutral worldで有限予算内の科学的帰無結論を形成できなかった。

このためv0.3ではendpointを次の階層へ再編する。

1. **Primary mechanism claim:** component-aligned needによる損傷targetへの証拠配分
2. **Mandatory safety gate:** neutral worldでのfalse repair
3. **Confirmatory secondary claim:** replicated restorationへの下流効果
4. **Mechanistic secondary endpoints:** selectivity、自己境界、no_bridge、validation、費用

この変更はdevelopment効果の最大化ではなく、回復・因果的正しさ・科学的帰無結論を分離するための概念修正である。

## 3. 固定architecture

- observation budget: **600**
- shift observation: **28**
- active sensing width: **2**
- memory-capacity reference: **320**
- primary cross-world memory: **OFF**
- internal variables: inherited canonical v0.14 generator
- self-boundary model: intervention-based causal model
- experiment selection within domain: common epistemic search
- repair decoder: need-blind common selector
- positive bridge: independent validation required
- null diagnosis: scoped `no_bridge` enabled
- replication: required for replicated-restoration endpoint

## 4. Primary conditions

### P1 actual_need

`need_i = P(i in causal core) × max(0, baseline_i − current_i)`に基づく、現在worldの実損傷と成分対応したneed。

### P2 yoked_need

同一generator stratumの別seedから得たactual need traceを用いる。各時点の総need量とdonor componentの時系列を保存し、固定された非ゼロcyclic derangementによってfocal worldの内部成分との対応を崩す。

### P3 curiosity

needを用いず、need-blind epistemic uncertaintyに基づいて領域配分・active sensingを行う。

### P4 no_need

needを用いない。shift後のself/neutral配分を50/50とし、active sensingにはcuriosityと同じneed-blind selectorを用いる。

すべてのprimary条件でdiagnosis、validation、repair、replication decoderは共通である。

## 5. World strata

v1 confirmationに含めるのは二層である。

- **W1 self_relevant:** 外部hidden mechanismと内部損傷に真のcausal bridgeがある
- **W2 neutral:** 外部異常と内部損傷が因果的に独立

`partial_bridge`は現実装にないためv0.3 confirmationから除外し、将来の独立拡張とする。

Generator stratumは次の組で固定する。

- core size
- topology
- grammar family
- primitive cardinality
- nonstationarity

## 6. Confirmatory seeds

- primary confirmatory focal seeds: **30000–30071**（N=72）
- bootstrap seed: **941731**
- bootstrap replicates: **50,000**
- development seeds 0–39はconfirmatory推定から除外

N=72は、generatorの9 strataを各6または12件で構成でき、neutral actual conditionでfalse repairが0件の場合にone-sided 95% Clopper–Pearson upper boundを5%未満にできる最小安全域を持つ候補として固定する。

Confirmatory donor mapはoutcomeを実行せず、seedとgenerator stratumだけから決定論的に生成し、pre-run manifestでhash固定する。

## 7. Primary endpointと操作チェック

### 7.1 Manipulation check

W1のpaired actual-minus-yoked:

- `mean_need_target_mass_share`

成立条件:

- paired mean > 0
- strata-preserving paired bootstrap 95% CI lower > 0
- yoked traceの各時点total need保存がmachine auditで成立
- component mappingにfixed pointがない

操作チェック不成立時、main mechanism verdictは`not_supported`とする。

### 7.2 Primary mechanism endpoint

W1のpaired actual-minus-yoked:

- `causal_target_sensing_share`

SESOI:

- **+0.08 absolute share**

`Supported`条件:

- paired mean ≥ +0.08
- strata-preserving paired bootstrap 95% CI lower > 0
- manipulation check成立
- mandatory safety gate成立
- actual/yoked exact replay rate = 100%

### 7.3 Mandatory safety gate

W2 actual_need:

- `false_repair`

安全margin:

- true false-repair rate ≤ **0.05**

成立条件:

- observed false-repair countに対するone-sided 95% Clopper–Pearson upper bound ≤ 0.05

補助安全endpoint:

- explicit `no_bridge`率のone-sided 95% lower bound ≥ 0.90

補助endpoint不成立だけではmain verdictを自動棄却しないが、帰無結論形成の限界として報告する。

## 8. Confirmatory secondary endpoint

W1のpaired actual-minus-yoked:

- `replicated_restoration`

SESOI:

- **+0.10 absolute probability difference**

`Supported`条件:

- paired mean ≥ +0.10
- strata-preserving paired bootstrap 95% CI lower > 0
- mandatory safety gate成立

これはprimary mechanism claimとは別に判定する。target sensingが支持され、replicated restorationがindeterminateまたはnot supportedである場合、論文の主張は「証拠配分を変えたが下流改善は確証されなかった」に限定する。

## 9. Key secondary endpoints

- `causal_target_sensing_selectivity`（initial SESOI +0.08）
- `mean_need_true_core_mass_share`
- `mean_sensed_need_mass_share`
- `self_domain_observation_share`（alignment endpointではない）
- causal self-boundary precision / recall
- bridge decision accuracy
- explicit `no_bridge`
- independent validation pass/fail
- exact / functional program discovery
- diagnosis observations
- total cost
- common-decoder replicated restoration

Secondary endpointsはprimary verdictを救済しない。

## 10. Exact replayとcommon decoder

Actual/yoked × W1/W2の全confirmatory source traceで実施する。

### Exact replay

source evidence prefixについて、次を完全一致させる。

- action sequence
- observations
- hidden side effects required for reconstruction
- diagnosis cut point

1件でも不一致ならmain mechanism verdictは`not_supported`とし、実装監査失敗として確認解析を停止する。

### Common decoder

need policy、condition ID、need vectorを受け取らない共通decoderをreplayed evidence prefixへ適用する。これは自然直接効果の推定ではなく、**trace-source mediation diagnostic**である。

## 11. Three-way verdict rules

### Main mechanism claim

- **supported:** §7.1、§7.2、§7.3、exact replayをすべて満たす
- **not_supported:** manipulationの方向が非正、target sensing meanが非正、safetyのone-sided lower boundがmarginを超える、またはexact replay <100%
- **indeterminate:** 方向は正だがCIが0を跨ぐ、point estimateがSESOI未満、またはsafety upper boundがmarginを超えるがlower boundは超えない

### Downstream replicated-restoration claim

- **supported:** mean ≥+0.10、CI lower >0、safety supported
- **not_supported:** meanが非正、CI upper ≤0、またはsafety not_supported
- **indeterminate:** それ以外

## 12. Actual vs curiosity / no_need

事前指定のsecondary comparisonとして同じpaired summaryとintervalを報告するが、main mechanism verdictには用いない。

- actual > curiosity: maintenance alignmentがpure epistemic controlを上回る条件
- curiosity > actual: need一般優位を否定し、探索範囲とのtrade-offとして報告
- no_need: difficulty/control baseline

## 13. Confirmatory ablations

Primary confirmation後、main verdictと独立に次を実行・報告する。各条件は指定されたworldのみでN=72とする。

- causal vs correlation self-model: W1
- actual vs no_null: W2
- actual vs no_bridge_validation: W2
- no_null_no_validation forced-positive interaction: W2
- actual vs passive_only: W1
- actual vs pair_limited: W1

Ablationは科学探究一般の必要条件を証明せず、このbenchmarkにおける機能分解として扱う。

## 14. Analysis

- sampling unit: paired focal seed
- resampling: generator stratum内paired bootstrap
- interval: percentile 95%
- bootstrap seed: 941731
- replicates: 50,000
- safety interval: one-sided 95% exact Clopper–Pearson
- missing run: automatic imputationなし
- duplicate/missing/unexpected run key: merge audit failure
- primary endpointの多重性: primary efficacy endpointは1本、safetyはmandatory gate
- downstream endpointは別のconfirmatory secondary claimとして明示

## 15. Claim boundary

Main mechanismがsupportedでも言えるのは次だけである。

> 設計者が規定した内部維持状態と因果的自己モデルに成分対応したneedが、特定の因果マイクロワールドにおいて、総need量を保ちながら成分対応を崩したyoked controlより、限られた能動センシングを実損傷対象へ配分した。

Downstreamもsupportedの場合にのみ、条件付きで診断・修復の改善を追加する。

以下は主張しない。

- 構成的自律性
- 内生的規範
- 構成的な死
- 自己形成された維持対象
- 外部問題領域の一般的形成
- 人間の科学探究の再現
- 一般的な科学者AI

## 16. STOP boundary

本書はfreeze candidateであり、confirmatory runnerはまだ有効化しない。次を満たすまでconfirmatory episodeを実行しない。

- source/runtime manifestとhashの最終確認
- condition、endpoint、world、seed、yoke、SESOI/verdict registryの相互一致
- 72-seed chunk execution planとexpected-key gridの固定
- analysis script 50,000-bootstrap smoke test
- pre-run manifest署名
- ユーザーによる明示的なPhase U1.5開始指示
