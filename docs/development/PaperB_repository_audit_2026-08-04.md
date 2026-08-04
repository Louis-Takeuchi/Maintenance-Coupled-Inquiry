# 論文B repository監査報告

**対象:** `constitutive_inquiry_mvp_v0_1`〜`v0_14` の14 ZIP  
**監査日:** 2026-08-04  
**目的:** 段階的な機構探索をコード根拠で整理し、論文Bの統一確認実験へ移行できる状態かを判定する。

## 1. 結論

1. **14版すべてを展開・読取でき、全版の自動テストが成功した。**
   - v0.1〜v0.5: `unittest`、1/5/6/7/7 tests PASS。
   - v0.6〜v0.14: `pytest`、6/7/11/13/10/11/13/14/20 tests PASS。
2. **最新の監査済み実装はv0.14である。** v0.14はソース凍結、800行の最終確認、重複キー0、代表条件の再実行一致を持つ。
3. ただし、**v0.14をそのまま論文B全体の正式版にはできない。** v0.14の条件は記憶転移の安全性に特化しており、論文Bの中心比較である `actual need / yoked need / curiosity / no need` が揃っていない。
4. v0.14の主要結果は「有益な記憶転移」ではなく、**vacuous safety（記憶を一度も使わない安全）**である。主条件はsparse resetと全指標で同一で、self-relevant 40世界中memory proposal実行0件だった。
5. よって、論文Bは次の二系統に分けるべきである。
   - **主確認系:** 維持信号→証拠配分→介入・修復を検証する `paperB-unified-v1`。
   - **記憶系:** v0.12〜v0.15の世界間転移。主確認から独立したsecondary/exploratory研究として扱う。

## 2. 配布物・再現性監査

### 2.1 ZIPとソース

- v0.1〜v0.14の全ZIPを展開可能。
- v0.14を新規展開した直後、`sha256sum -c SHA256SUMS.txt` は全項目PASS。
- テスト実行後は`.pyc`のハッシュだけが変化し、`SHA256SUMS.txt`全体検証は失敗する。一方、全`.py`・全テストソースは一致した。

**修正事項:** 公開版の配布ハッシュから`__pycache__/*.pyc`を除外し、実行ソースmanifestと結果manifestを分離する。

### 2.2 メタデータ上の既知問題

- v0.13はプロジェクト名がv0.13だが、`pyproject.toml`のnumeric versionが`0.12.0`のまま。READMEで既知問題として記録済み。
- v0.14の`confirmation_analysis_plan_v0_14.md`はtraining budgetを360と記載するが、READMEと実際の`training_run_summaries.csv`は320。全32行が`steps_survived=320, completion_rate=1.0`であり、**実行値は320**と判定する。
- v0.14では、17000–17039の予備確認がruntime mismatchにより棄却され、18000–18039だけが正式確認に使われた。これは適切に記録されている。

## 3. v0.14 file tree（主要部）

```text
constitutive_inquiry_mvp_v0_14/
├── README.md
├── pyproject.toml
├── run_experiment.py
├── run_mode_v0_14.py
├── run_training_chunk_v0_14.py
├── run_reproduction_audit_v0_14.py
├── analyze_v0_14.py
├── src/constitutive_inquiry/
│   ├── environment.py
│   ├── self_model.py
│   ├── model.py
│   ├── agent.py
│   ├── crossworld.py
│   ├── experiment.py
│   └── metrics.py
├── tests/
│   ├── test_environment.py
│   ├── test_self_model.py
│   ├── test_model.py
│   ├── test_agent.py
│   └── test_crossworld.py
├── docs/
│   ├── design_spec_v0_14.md
│   ├── confirmation_analysis_plan_v0_14.md
│   ├── evaluation_note_v0_14.md
│   ├── provenance_audit_v0_14.md
│   ├── freeze_audit_v0_14.txt
│   └── next_steps_v0_15.md
└── results/
    ├── training/
    ├── confirmation/
    ├── confirmation_run_summaries.csv
    ├── primary_target_results.csv
    ├── key_evaluation_contrasts.csv
    ├── mapping_trust_summary.csv
    └── reproduction/
```

## 4. version map

| 版 | 追加した中心機構 | 主要結果 | 論文上の扱い |
|---|---|---|---|
| v0.1 | 最小Boolean world | 全条件が容易に回復。環境が簡単すぎた | sanity / exploratory |
| v0.2 | 複数regime、コスト・ノイズ、維持資源 | maintenanceはenergyを保存したがcuriosityより発見性能は上がらない | exploratory held-out |
| v0.3 | latent variable proposalとinstrument build | generationは初期仮説外の法則を回復。sham≈maintenance | 生成機構の局所確認 |
| v0.4 | 4 world class、actual vs matched sham、evidence matching | generationとpersistenceは支持。actual need固有の発見優位なし | factorial exploration |
| v0.5 | self-relevant vs neutral | actual need×self-relevanceの正のinteraction | need alignmentの初期証拠 |
| v0.6 | unlabeled internal state、因果的自己境界 | causal modelはcorrelation modelより高精度。actual>yokedだがcuriosity/oracleがactualを上回る | 自己境界機構 |
| v0.7 | needとinformation valueの二段階制御 | actual 0.93、curiosity 0.92、yoked 0.50。matched replay 0.93 | **主確認の直接的前身** |
| v0.8 | no_bridge、active internal sensing | neutral false repairを0.96→0.10に低減。ただしexplicit nullは2/100 | abstention開発 |
| v0.9 | reversible gate causal test | neutral explicit no_bridge 0.93、false repair 0。actual=yoked=curiosity=1.00 | null discovery確認 |
| v0.10 | 2操作の複合介入、validation、replication | restoration 0.94、replication 0.93、false repair 0 | composite intervention確認 |
| v0.11 | 長さ1–4の順序依存program search | restoration/replication 0.99、探索空間3.31%。actual=yoked | 最も安定したlocal-search基盤 |
| v0.12 | cross-world macro memory | persistent 0.99 vs reset 0.61。ただしscalar singleton alignment shortcutあり | 条件付き正の転移 |
| v0.13 | relational alignment、decoy、shortcut除去 | memory 0.875 vs reset 1.00。negative transfer | 確認済み負の結果 |
| v0.14 | posterior gate、local beam、quarantine/rollback | memory非使用で安全。sparse resetと完全同一 | 最新監査版・vacuous safety |
| v0.15 | 計画のみ | hidden applicability、calibration、non-vacuous coverageを予定 | 未実装 |

詳細は同梱の`PaperB_version_map.csv`を参照。

## 5. v0.14環境の正確な構成

### 5.1 外部因果世界

- 入力: 4つの二値変数 `x0..x3`。
- baseline rule: `x0 XOR x1 XOR (x2 AND x3)`。
- hidden mechanisms: `m0..m3`。特定の入力条件でbaseline出力を反転する。
- domain: `self`と`neutral`。
- `self_relevant`: causal mechanismがmediatorとdamaged core variableを直接・遅延的に悪化させる。
- `neutral`:同じ外部mechanismと同じ内部悪化が存在するが、内部悪化は独立scheduleによる。

### 5.2 内部状態

- `N_INTERNAL = 14`。
- evaluationのcore sizeは5または6、topologyはring/chain/dense。
- shuffled core内の最初の3変数がresource、memory、sensor。
- mediatorとdamaged variableもcore内から選ばれる。
- 非coreには、core mean readout、lagged readout、oscillator、random walk、stable attractor、追加distractorがある。
- 初期値は概ね0.925付近。
- memory値は保持可能観測数を24〜budgetへ写像する。
- sensor低下は観測反転確率を増加させる。
- 死亡条件は`min(core)<=0.055`または`mean(core)<=0.15`というコード上の規定。

### 5.3 自己境界学習

- shift前は全14変数を観測できる。
- 各内部変数へpulseを与え、他変数への伝播を記録する。
- causal scoreは、その変数をpulseしたときの他変数低下からbackground pulse effectと0.0025を引いた正部分の和。
- scoreを2-cluster BICで分割し、logistic変換で`P(variable is core)`を得る。
- need vectorはコード上、

```text
need_i = core_probability_i × max(0, baseline_i - last_seen_i) / 0.30
```

- post-shiftはpassive 2変数＋有料active sensingで内部状態を取得する。

### 5.4 介入言語

- primitive poolは`p0..p7`。
- evaluation worldでは5操作または7操作が利用可能。
- canonical rolesはA–F、7操作worldにはdecoy Xを追加。
- singleton effectはA/B、C/D、E/Fで同値にされ、単一操作の順位だけではrole alignmentできない。
- directed pair relationがrole fingerprintを担う。
- intervention program長は最大4。
- familyはtraining: repeat/delayed/inhibitor_first/fork、held-out: branch_comp/context_comp。

### 5.5 bridge、repair、replication

- external suppressionとinternal damage reductionの両方を観測してbridge/no_bridgeを判定する。
- positive bridge候補は別関数`validate_bridge`で12 trialの独立matched exposure検証を受ける。
- validation criterionはintervention strength≥0.64かつdamage effect≥0.014。
- repairはpermanent external interventionとrestore operatorを組み合わせる。
- repair後、環境shiftを加えた12 trial replicationを行う。

## 6. agent decision loop

```text
1. need vectorを計算
2. shift前: internal pulseでself-boundary learning
3. shift後: needに基づきself/neutral domainの証拠配分を決定
4. mechanism survey
5. singleton calibration
6. directed pair calibration
7. bounded beam searchでprogram探索
8. external suppressionとinternal effectからbridge/no_bridge診断
9. positive bridgeなら独立validation
10. validation成功時のみrepair
11. fresh challengeでreplication
12. memory条件では成功/失敗に応じてregister, quarantine, rollback, decay
```

重要なコード上の注意:

- v0.14の全modeは実質的にactual needを使用する。`curiosity`/`yoked` modeは存在しない。
- needはdomain allocationだけでなく、restore operator選択にも使われる。
- よって「needの効果は証拠取得だけ」と結論するには、repair readoutをneed-blindにしたreplay/common-decoder解析が必要。

## 7. v0.14 condition table

| Condition | Memory | Gate | Local beam | Quarantine/rollback | 用途 |
|---|---:|---:|---:|---:|---|
| confidence-gated | correct | yes | yes | yes | principal |
| ungated | correct | no | not protected | online | active-transfer control |
| full reset | none | — | full calibration | — | local baseline |
| sparse reset | none | — | sparse calibration | — | matched no-memory control |
| posterior no quarantine | correct | yes | yes | no | failure-handling ablation |
| no local reservation | correct | forced/open | no | yes | local protection ablation |
| frozen correct | correct | yes | yes | no revision | memory revision control |
| adversarial wrong | wrong | yes | yes | yes | adversarial safety control |
| oracle | true program | — | — | — | upper bound |
| forced positive | correct | yes | yes | yes; no null | no_bridge ablation |

## 8. metric table

### Primary behavioral endpoints

- `organization_restored`: correct repairかつfinal minimum core≥0.55。
- `replicated_restoration`: restoredかつreplication success。
- `false_repair`: neutral worldでrepairを1回以上実行。
- `explicit_no_bridge`:最初の診断がno_bridge。
- `decision_correct`: self-relevantではrestored、neutralではrepairなし。

### Epistemic endpoints

- mechanism/bridge decision correctness。
- exact/functional intervention program。
- validation attempted/passed/effect。
- evidence rowsとtested scope declaration。
- core precision/recall。

### Cost・search endpoints

- unique sequences evaluated。
- intervention-space fraction。
- diagnosis/restoration observations。
- total cost、steps survived。

### Memory endpoints

- mapping trust、alignment entropy、held-out support。
- memory proposal tested。
- memory changed action。
- wrong memory detected before repair。
- local beam reserved。
- quarantine count。

## 9. v0.14 official resultの再確認

raw CSVから以下を再確認した。

- 800 rows。
- 10 modes × 40 seeds × 2 relevance。
- seed range 18000–18039。
- `(mode, seed, relevance)`の重複0。
- principal self-relevant restoration 40/40。
- principal neutral false repair 0/40。
- sparse reset self-relevant restoration 40/40。
- principalとsparse resetのmean sequencesはともに45.125。
- principal memory proposal tested 0/40、memory changed action 0/40。
- ungated memory changed action 18/40、restoration 38/40。
- no-local-beam memory changed action 34/40、restoration 21/40。
- forced-positive neutral false repair 40/40。

したがって、v0.14の正しい結論は次である。

> confidence gateはnegative transferを防いだが、memoryを完全に無効化した。改善はsparse current-world calibrationによるもので、cross-world memoryの有益性は支持されない。

## 10. known failure modes

1. **benchmark too easy / ceiling:** v0.1、v0.9〜v0.11で条件差が消失。
2. **resource conservation≠scientific discovery:** v0.2、v0.4。
3. **sham signalでもgeneration可能:** v0.3、v0.4。
4. **need-only narrowing:** v0.6。urgent deficitへ集中しcausal coverageを失う。
5. **false causal self-story:** v0.7。no_bridgeなしでneutral repairが増える。
6. **abstention≠positive null:** v0.8。行動しないだけでno_bridgeを確立しない。
7. **observational caution≠causal null:** v0.9。reversible interventionが必要。
8. **bounded-language shortcut:** v0.10〜v0.12。固定primitive ontologyとprogram familyに依存。
9. **scalar alignment shortcut:** v0.12。singleton rankでworld間対応が容易。
10. **negative transfer:** v0.13。decoyを含むrelational alignment uncertaintyが探索を誤誘導。
11. **vacuous safety:** v0.14。gateがmemoryを一度も通さない。
12. **protected local beam依存:** local reserve除去でrestoration 52.5%。
13. **metadata/provenance fragility:** v0.13 version mismatch、v0.14 budget記載矛盾、`.pyc`を含む全体hash。

## 11. exploratory / confirmatoryの区別

### 累積研究プログラムとして

v0.1〜v0.14は、前版の失敗を見て次版の環境・機構・endpointを変更している。したがって、**系列全体はexploratory mechanism development**である。

### 各版の内部では

v0.3以降の多くはdevelopment seedとheld-out/final seedを分け、v0.9以降はsource freezeとprovenance auditも持つ。これらは、**その版で固定した狭い仮説に対するversion-local confirmation**として扱える。

### 論文Bでの表現

- 「v0.9でno_bridgeの有効性を確認した」のように版限定で書く。
- 「一連の実験が構成的自律性仮説を確認した」と統合してはならない。
- 論文の中心主張は、未使用worldで実施する新しいpaper-level confirmatory runに依拠させる。

## 12. 正式候補versionの判定

### v0.14を採用できる部分

- environment、causal self-model、partial observation、active sensing。
- explicit no_bridge、reversible intervention、bridge validation。
- ordered program search、repair、replication。
- results schema、freeze/provenance procedures。

### v0.14をそのまま採用できない部分

- condition setがmemory transfer専用。
- actual/yoked/curiosity/no-need比較がない。
- high-performing sparse searchがceilingを作る。
- needがrepair operator選択にも入るため、evidence acquisition effectを単独同定できない。

### 判定

> **v0.14は「実装部品のcanonical source」だが、「論文B全体のcanonical experiment」ではない。**

新しい正式候補は、v0.14からprimary memory policyを外し、need policyを独立factorとして復元した`paperB-unified-v1`とする。

## 13. 次工程

1. v0.14をread-only baselineとして保存。
2. 新branch `paperB-unified-v1`を作成。
3. conditionをpolicy factorとmechanism ablationへ分離。
4. developmentではoracle/random/forced-positiveだけを見て難易度を校正し、actual-vs-yoked差は見ない。
5. protocol、endpoint、seed ranges、manifestを凍結。
6. unused confirmation worldsで実行。
7. v0.15 memory研究は主確認後、別branchで実施。

