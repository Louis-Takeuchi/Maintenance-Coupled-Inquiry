# 論文B v0.3 freeze candidate 完了報告

**日付:** 2026-08-04  
**状態:** `PASS_LOCKED_NOT_ACTIVATED`  
**確認実験episode:** 0件

## 結論

`paperB-unified-v1`は、統一確認実験の**実行直前freeze candidate**まで到達した。確認seedは封印され、activation manifestは存在せず、confirmatory runnerはepisode生成前に停止する。

## 正式候補の中心設計

- observation budget: 600
- shift observation: 28
- active sensing width: 2
  - maintenance-priority slot: 1
  - protected epistemic slot: 1
- primary memory: OFF
- primary conditions: actual_need / yoked_need / curiosity / no_need
- worlds: W1 self_relevant / W2 neutral
- `partial_bridge`: v0.3から除外し将来拡張へ延期
- confirmatory focal seeds: 30000–30071（N=72）
- primary source episodes: 576
- actual/yoked replay episodes: 288
- ablation episodes: 432
- bootstrap: seed 941731 / 50,000 replicates

## Endpoint階層

1. **Primary mechanism:** `causal_target_sensing_share`、actual − yoked、SESOI +0.08
2. **Mandatory safety gate:** actual_need neutral worldの`false_repair`絶対率、one-sided 95% upper ≤0.05
3. **Confirmatory secondary:** `replicated_restoration`、actual − yoked、SESOI +0.10
4. **Supporting safety:** `explicit_no_bridge`、one-sided 95% lower ≥0.90

## Development evidence

40 development seedsのW1では、actual − yokedの差は次の通りだった。

- damaged-target sensing share: +0.1222、95% diagnostic interval [0.0867, 0.1614]
- target sensing selectivity: +0.1092、[0.0669, 0.1534]
- replicated restoration: +0.35、[0.15, 0.55]

W2 actual_needのfalse repairは0/40だったが、one-sided 95% upper boundが約0.072で0.05を下回らないため、development verdictは安全性についてindeterminateのままである。このためN=72を固定した。

六seed budget-600 auditでは、need-blind common decoderが24/24 traceでsourceと一致した。W1 replicated restorationはactual 6/6、yoked 3/6、W2は両条件ともno_bridge 6/6、false repair 0/12だった。これは開発段階で、差がpolicy固有decoderではなく取得証拠の差から再現されることを示す診断であり、確認結果ではない。

## Freeze監査

- 45/45 tests PASS
- 20/20 freeze-readiness checks PASS
- frozen files 65/65 SHA-256一致
- 320-row development grid: duplicate 0 / missing 0 / unexpected 0
- activation manifest absent
- lock probe: exit code 1、出力生成なし
- freeze manifest SHA-256: `4cdc7c3f5e209eb193a83a3bae759df0f98a18571bd833ac1d5edaf6a1c7ae3f`

## 次のSTOP

現段階では確認実験を実行しない。次工程は、freeze candidateの内容を人間が確認した後、確認実験開始を別途明示的に承認し、現pre-run manifestとfreeze hashに結びついたactivation manifestを作成することである。
