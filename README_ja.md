# Maintenance-Coupled Inquiry（維持結合型探究）

[![tests](https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/actions/workflows/tests.yml/badge.svg)](https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/actions/workflows/tests.yml)
[![release](https://img.shields.io/github/v/release/Louis-Takeuchi/Maintenance-Coupled-Inquiry?label=release)](https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/releases/tag/v1.0.0)
[![code license](https://img.shields.io/badge/code%20license-Apache--2.0-blue.svg)](LICENSE)
[![data%20%26%20docs license](https://img.shields.io/badge/data%20%26%20docs-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)

構成要素に整列した維持信号が、有限の探究予算下で証拠配分、因果診断、再現確認付き回復を変えるかを検証した、事前登録型の計算実験です。

**リポジトリ状態:** 公開再現パッケージ  
**バージョン:** 1.0.0  
**論文状態:** 原稿作成済み・未出版  
**ライセンス状態:** CodeはApache-2.0、data・原稿・文書・図はCC BY 4.0  
**最新リリース:** [v1.0.0](https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry/releases/tag/v1.0.0)  
**English:** [README.md](README.md)

## 対象範囲と主張境界

本研究は、制約された因果マイクロワールドにおける機能的な計算実験です。支持されたのは、次の限定された知見です。

- 構成要素整列型need信号によって証拠配分が変化した。
- `actual_need`は、総need量を保存し整列だけを崩した対照needである`yoked_need`を上回った。
- actual needで再現確認付き回復（replicated restoration）が改善した。
- condition IDもneed vectorも受け取らないcommon decoderでも、証拠traceの差が残った。
- neutral worldにおける誤修復（false repair）の事前指定安全gateを通過した。

一方で、構成的自律性、内生的規範性、構成的な死、生物学的個体性、一般的な自律科学者、人間水準の認知を実現したことは支持しません。need変数、viable range、損傷、修復、介入語彙、停止規則はいずれも設計者が規定しています。詳細は[CLAIM_BOUNDARY.md](docs/CLAIM_BOUNDARY.md)を参照してください。

## 主な確認実験結果

以下の値は、凍結CSVとintegrity auditから再照合しました。

| 指標 | 凍結結果 |
|---|---:|
| Confirmatory seeds | 72 |
| Primary source runs | 576 |
| Ablation source runs | 432 |
| Exact replay | 288/288 |
| Target sensing差（actual − yoked） | +0.1173 |
| 95% stratified paired bootstrap CI | [+0.0722, +0.1632] |
| 事前指定SESOI | +0.08 |
| Actual replicated restoration | 41/72 |
| Yoked replicated restoration | 20/72 |
| 対応差 | +0.2917 |
| Neutral worldのactual false repair | 0/72 |
| 片側95% exact上限 | 0.0408 |

actual conditionの再現確認付き回復は41/72であり、すべてのworldに成功したわけではありません。支持されたのはyoked controlに対する確率的改善であり、完全または一般的な因果能力ではありません。詳細は[RESULT_SUMMARY.md](docs/RESULT_SUMMARY.md)にあります。

## リポジトリ構成

| パス | 役割 |
|---|---|
| [`manuscript/`](manuscript/) | 公開URLを反映したMarkdown正本、DOCXスナップショット、機械可読表 |
| [`supplement/`](supplement/) | Supplementary MaterialsのMarkdownとDOCXスナップショット |
| [`figures/`](figures/) | 論文・補足図のPDF/PNG |
| [`protocol/`](protocol/) | 凍結確認protocolとfreeze-readiness資料 |
| [`src/`](src/) | バイト列を保持した凍結v0.3 Python package |
| [`scripts/`](scripts/) | 凍結runner、保存済みpost-run解析、公開用検証helper |
| [`tests/`](tests/) | 凍結unit tests |
| [`manifests/`](manifests/) | seed、yoke、chunk、endpoint、SESOI、activation、freeze manifest |
| [`data/processed/`](data/processed/) | primary/ablationのmerged confirmatory data |
| [`data/analysis/`](data/analysis/) | endpoint、common decoder、ablation、verdict、summary出力 |
| [`data/execution_receipts/`](data/execution_receipts/) | 120件すべての変更していないexecution receipt |
| [`docs/development/`](docs/development/) | 開発phaseとrepository auditの記録 |
| [`legacy/`](legacy/) | historical v0.14 baseline（論文実装ではない） |

正本・生成物・archiveの関係は[FILE_MAP.md](docs/FILE_MAP.md)にまとめています。

## Quick start

凍結packageはPython **3.11以上**を指定しており、runtimeの外部依存はありません。テストにはpytestを使います。

```bash
git clone https://github.com/Louis-Takeuchi/Maintenance-Coupled-Inquiry.git
cd Maintenance-Coupled-Inquiry
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
python scripts/verify_public_results.py
```

凍結suiteは45テストです。結果検証helperは読み取り専用で、公開CSVに対してrun数と主要値を照合します。

## 解析の再現

正本の凍結出力を上書きせず、主要endpoint、common decoder、ablationの5表を`build/`へ再生成できます。

```bash
python scripts/reproduce_processed_analysis.py --output build/reproduced-analysis
python scripts/compare_reproduced_analysis.py build/reproduced-analysis
```

入力は`data/processed/`のmerged confirmatory dataです。元のpost-run解析scriptは`/mnt/data/paperB-unified-v1`という実行時container pathを含むため、`scripts/archived_postrun/`にバイト列を変えずprovenanceとして保存しています。

提供された公開packageには図生成source scriptが含まれていません。公開済みPDF/PNGは`figures/`にありますが、現時点ではコードからの図の完全再生成を主張できません。

解析だけの再現はmerged summariesを読み、固定seedによる50,000反復bootstrapを実行します。確認実験全体の再実行は、1,008 source runと288 replay caseを実行する別工程です。凍結activation、chunk、seed、yoke manifestを変更してはいけません。実行前に[REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md)を確認してください。

## データ公開範囲

Gitでは、merged primary/ablation run summaries、endpoint表、解析出力、integrity audit、execution receiptを管理します。v1.0.0 Releaseには検証済みall-in-one package、cleaned legacy archive、および各checksum fileを収録します。別個のcore ZIPは含めず、未検証の推測から再構成しません。

完全なstep-level traceは、main Git historyにも現在の検証済みpackageにも含まれていません。以前のfull-trace ZIPはarchive integrity検証に失敗したため除外されました。trace再生成に必要な凍結codeとmanifestは提供していますが、「すべてのraw step traceを公開済み」と主張するには、新しい検証済みdepositが必要です。

## 過去バージョン

v0.14は、統一前のhistorical baselineとして保存されています。最終確認結果を生成した実装ではなく、論文のcanonical implementationとして扱ってはいけません。

v0.1–v0.13はmain implementationではなくdevelopment provenanceです。cleaned archiveはmain treeではなくRelease assetです。詳細は[LEGACY_VERSIONS.md](docs/LEGACY_VERSIONS.md)を参照してください。

## 引用

[`CITATION.cff`](CITATION.cff)と[`manuscript/`](manuscript/)の論文titleを参照してください。論文は未出版であり、journal volume、issue、page、article DOI、archive DOIは確定していません。ORCID、所属、DOI、投稿情報は将来追加するmetadataとして[`PUBLICATION_OPEN_FIELDS.md`](PUBLICATION_OPEN_FIELDS.md)に記録しています。

## AI assistance disclosure

OpenAI ChatGPTは英訳、構造編集、文書整形を補助しました。著者が科学的主張、計算、参考文献、最終表現を確認し、内容に責任を負います。AIが自律的に研究判断を行った、または確認実験を無監督で実施したとは主張しません。

## ライセンス

| 対象 | ライセンス |
|---|---|
| Code（`src/`、`scripts/`、`tests/`、Python設定、CI） | [Apache License 2.0](LICENSE) |
| Data、manifest、CSV出力、execution receipt | [CC BY 4.0](LICENSE-DATA) |
| 原稿、supplement、文書、図、README、protocol文書 | [CC BY 4.0](LICENSE-DOCS) |

第三者資料には各権利者・各ライセンスの条件が適用されます。適用範囲は[`NOTICE.md`](NOTICE.md)を参照してください。
