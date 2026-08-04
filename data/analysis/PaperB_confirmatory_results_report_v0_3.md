# 論文B 確認実験結果報告 v0.3

**実行日:** 2026-08-04  
**Protocol:** `v0.3`  
**状態:** `CONFIRMATORY_EXECUTION_COMPLETE`  
**Main mechanism verdict:** **SUPPORTED**  
**Downstream replicated-restoration verdict:** **SUPPORTED**

---

## 1. 結論

凍結済みv0.3プロトコルの判定規則では、主機構claimと下流replicated-restoration claimの両方が支持された。

支持された主張は、次の限定された機能的主張である。

> 設計者が規定した内部維持状態と因果的自己モデルに成分対応したneedは、特定の因果マイクロワールドにおいて、総need量を保ちながら成分対応だけを崩したyoked controlより、限られた能動センシングを実際の損傷対象へ多く配分した。その証拠traceの差は、共通decoder下でも因果判断とreplicated restorationの差として残った。

この結果は、構成的自律性、内生的規範、構成的な死、自己形成された維持対象、一般的な科学者AIを示すものではない。

---

## 2. 実行完整性

### Source runs

- primary: **576**
- confirmatory ablations: **432**
- source runs合計: **1,008**
- exact replay/common-decoder対象: **288**

### Key audit

- primary expected keys: **576/576**
- ablation expected keys: **432/432**
- duplicate keys: **0**
- missing keys: **0**
- unexpected keys: **0**
- execution receipts: **120/120**
- exact replay: **288/288 = 100%**
- post-run automated tests: **45/45 PASS**
- frozen files changed after activation: **0**

全receiptは同一のactivation hashとfreeze-candidate hashに結び付いている。

- activation SHA-256: `3cc3553400e935d3cce66a2dcb34b90697b19f86109cf74eeed87e0e3fb8ad24`
- freeze manifest SHA-256: `4cdc7c3f5e209eb193a83a3bae759df0f98a18571bd833ac1d5edaf6a1c7ae3f`

---

## 3. Manipulation check

W1におけるactual-minus-yokedのdamaged target need mass差は次のとおりだった。

| Endpoint | N | Mean difference | 95% stratified paired bootstrap CI |
|---|---:|---:|---:|
| `mean_need_target_mass_share` | 72 | **+0.0876** | **[+0.0609, +0.1148]** |

CI下限が0を上回り、actual needがfocal damaged componentへ整列し、yoked needでその整列が崩れていることを確認した。

---

## 4. Primary mechanism endpoint

| Endpoint | N | Actual−yoked | 95% CI | SESOI |
|---|---:|---:|---:|---:|
| `causal_target_sensing_share` | 72 | **+0.1173** | **[+0.0722, +0.1632]** | +0.08 |

事前規則は「point estimateが+0.08以上、CI下限が0より大きい、manipulation・safety・replayが成立」である。すべてを満たしたため、main mechanism claimは`SUPPORTED`となった。

Key secondaryのtarget selectivityも正方向だった。

| Endpoint | Actual−yoked | 95% CI |
|---|---:|---:|
| `causal_target_sensing_selectivity` | **+0.1020** | **[+0.0491, +0.1556]** |

---

## 5. Mandatory safety gate

Neutral worldにおけるactual needの安全性は次のとおりだった。

- false repair: **0/72**
- one-sided 95% exact upper bound: **0.0408**
- frozen safety margin: **0.05**
- safety verdict: **SUPPORTED**

補助安全endpoint:

- explicit `no_bridge`: **71/72**
- one-sided 95% exact lower bound: **0.9358**
- frozen lower-rate基準: **0.90**

したがって、primary mechanism claimに必要なmandatory safety gateを通過した。

---

## 6. Downstream replicated restoration

W1のreplicated restorationは次のとおりだった。

- actual need: **41/72 = 56.9%**
- yoked need: **20/72 = 27.8%**
- paired difference: **+0.2917**
- 95% CI: **[+0.1667, +0.4167]**
- SESOI: **+0.10**

事前規則を満たしたため、downstream replicated-restoration claimは`SUPPORTED`となった。

ただし、actual needも41/72であり、全worldに成功したわけではない。W1でのbridge decision correctは44/72で、28/72ではexplicit `no_bridge`となった。したがって、結果は「性能が完全になった」ではなく、「yoked controlより確率的に改善した」と解釈する。

Diagnosis observationsのactual-minus-yoked差は−8.21観測だったが、95% CIは[−22.56, +5.68]で0を跨いだ。診断速度の改善は明確ではない。

---

## 7. Common decoder

actual/yokedのsource traceを、condition ID、need policy、need vectorを受け取らない共通decoderへ入力した。

### W1

| Endpoint | Actual trace−yoked trace | 95% CI |
|---|---:|---:|
| common-decoder bridge correct | **+0.3194** | **[+0.1944, +0.4444]** |
| common-decoder replicated restoration | **+0.2778** | **[+0.1528, +0.4028]** |
| common-decoder false repair | 0.0000 | [0.0000, 0.0000] |

Common-decoder replicated restorationはactual trace **40/72**、yoked trace **20/72**だった。

この結果は、actual/yoked差がcondition-specific repair formulaだけで生成されたのではなく、取得されたevidence traceの違いに担われているというmediation diagnosticと整合する。ただし、自然直接効果の推定ではない。

### W2

Common decoder false repairはactual/yokedとも0だった。Bridge-correct差は−0.0694でCIが0を跨いだため、neutral traceでactualのdecoder精度が高いとは言えない。

---

## 8. Curiosity・no_needとのsecondary comparison

これらは事前指定secondaryであり、main verdictには使用していない。

### Actual vs curiosity

- target sensing share: **+0.1129** [0.0754, 0.1525]
- target sensing selectivity: **+0.0987** [0.0553, 0.1442]
- replicated restoration: **+0.2639** [0.1389, 0.3889]
- bridge decision correct: **+0.2778** [0.1528, 0.4028]
- diagnosis observations: **+10.28** [−2.07, 22.92]

Actualはcuriosityよりtarget sensingとrestorationで高かったが、診断が速いとは確認できなかった。

### Actual vs no_need

- target sensing share: **+0.1129** [0.0754, 0.1525]
- target sensing selectivity: **+0.0987** [0.0553, 0.1442]
- replicated restoration: **+0.3333** [0.1806, 0.4722]
- bridge decision correct: **+0.3194** [0.1667, 0.4722]
- diagnosis observations: **−99.04** [−118.10, −80.63]

No-need baselineに対しては、target sensing・restoration・診断観測数のすべてで明確な差があった。

---

## 9. Confirmatory ablations

Ablationは一般的必要条件の証明ではなく、このbenchmark内の機能分解として解釈する。

### 9.1 Correlation self-model

- core precision: correlation **0.457**、actual causal modelは約**0.938**
- actual−correlation precision差: **+0.4810** [0.4566, 0.5051]
- replicated restoration: correlation **17/72**、actual **41/72**
- paired差: **+0.3333** [0.2222, 0.4583]

Correlation modelはrecallを比較的保ったが、周辺変数を自己へ含めることでprecisionが大きく低下した。

### 9.2 `no_null`

Neutral worldで`no_bridge`候補を除去すると:

- diagnosis: **0/72**
- explicit `no_bridge`: **0/72**
- false repair: **0/72**

つまり、false positiveを起こさず停止した一方で、科学的帰無結論を形成できなかった。安全な未決定と明示的な`no_bridge`を区別する必要がある。

### 9.3 No independent bridge validation

- false repair: **19/72 = 26.4%**
- repair attempted: **19/72**
- organization restored: **18/72**

Actualとの差はfalse repairで−0.2639 [−0.3472, −0.1806]だった。Validationの除去により、見かけ上内部値が改善する事例を含めて誤った因果repairが増えた。

### 9.4 `no_null_no_validation`

- false repair: **72/72**
- repair attempted: **72/72**
- organization restored: **70/72**
- replicated restoration: **66/72**
- correct decision: **0/72**

内部値の回復率が高くても、外部異常と内部損傷のbridgeが存在しないため、全例がfalse repairである。これは「回復」と「因果的正しさ」を分ける必要性を示す。

### 9.5 Passive only

- diagnosis: **0/72**
- bridge correct: **0/72**
- replicated restoration: **0/72**

現在のmicroworldでは、受動観測だけではbridge識別に到達しなかった。

### 9.6 Pair limited

- exact/functional program: **0/72**
- diagnosis: **0/72**
- replicated restoration: **0/72**

長さ3以上のheld-out programを含む設計に対し、長さ2以下の探索制約はconstruct floorとなった。

---

## 10. 凍結解析CLIの表記上の問題

凍結済み`analyze_confirmatory_candidate.py`は、数値計算とverdict formulaを正しく適用したが、出力列`analysis_scope`に開発時の固定文字列`development_diagnostic_only`を残していた。

対応:

1. 凍結CLIの生出力をそのまま保存した。
2. 数値、bootstrap seed、replicate数、SESOI、verdict formulaを変更せず再現した。
3. `confirmatory_verdict.csv`ではscope表記のみ`confirmatory_primary_v0_3`へ訂正し、この事実をnote列に記録した。
4. 実行コードや凍結ファイルは結果確認後に変更していない。

これはreporting metadata defectであり、主要数値や判定を変更しない。ただし次版では、開発用と確認用の出力labelを事前に分離すべきである。

---

## 11. 実行中断のprovenance

最初のP000試行はツール側の5分上限で中断され、run summaryやexecution receiptを生成する前に停止した。生成されていたのはregistryファイルだけだった。

このpartial directoryは正式結果から隔離し、`v0_3_failed_attempts/P000_timeout_20260804T1228Z`として保存した。その後、同じ凍結コード・同じchunk IDを正式出力先へ再実行し、receipt付きで完了した。Partial出力はmerge・解析に使用していない。

---

## 12. Claim boundary

この確認実験が支持したのは、設計者が定義した内部維持信号による**機能的な探究制御**である。

支持しない主張:

- 構成的自律性を実現した
- 規範が系自身から完全に生じた
- 構成的な死を実装した
- 自己の維持対象を自己形成した
- 任意環境へ一般化する科学者AIを実現した
- 人間の科学探究を再現した

次の論文化では、主機構、下流効果、安全性、common decoder、ablation、絶対成功率の限界を分けて記述する必要がある。
