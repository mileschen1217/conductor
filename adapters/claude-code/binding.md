# Capability-tier binding — Claude Code

L1 names mechanisms; this file holds the values. 查證日期 **2026-07-11**（官方
文件對這些介面可能無聲變動）。

| 能力階層 | 模型/agent | 適用任務形 |
|---|---|---|
| frontier | fable（`claude-fable-5`）；opus（`claude-opus-4-8`）次選 | 首次診斷、架構取捨、跨檔不變量；通常即 commander 自身 |
| mid | sonnet（`claude-sonnet-5`）；唯讀 fan-out 用 `Explore` agent type | 規格清楚的實作、搜尋/盤點、多源研究、審查 lens。預設工人 |
| cheap | haiku（`claude-haiku-4-5-20251001`） | 已解模式批次套用、格式轉換、機械枚舉 |

tier-0 不入表：tier-0 是 script，不經 Agent tool。

## Worker tier（doctrine § Defaults「worker tier」的 CC 綁定）

opus commander → sonnet worker 為預設。

**haiku 作 worker 的准入——三條件全中才合法**：(1) brief 純機械、零殘留判斷；
(2) 有便宜的可執行 check artifact，失敗由機器抓而非自報；(3) 小而多的子任務，
單次重派成本有界。

`[unverified]` haiku-as-worker 在本專案樣本數 0；上列三條件是推理，不是實測。

## 價格比 r（doctrine「the brake」r 項的 CC 綁定）

**Per-pair 列，非 tier 粒度**：frontier tier 內部有 2× 價差。
r = worker output 牌價 ÷ commander output 牌價。

| r[worker←cmd] | fable cmd（$50/Mtok out） | opus cmd（$25） | sonnet cmd（$15） |
|---|---|---|---|
| worker = sonnet（$15） | 0.3 | 0.6 | 1.0 |
| worker = haiku（$5） | 0.1 | 0.2 | 0.33 |

單位權重（token 種類換算成 output-token 等值）：
`weight[output]=1, weight[cache-write]=0.25, weight[input]=0.2`

**Re-pin 2026-08-05（r_rev 引用點）** —— sonnet 依標準價 $3/$15 入表。原
introductory pricing（$2/$10）雖排程 2026-09-01 到期，帳單證據顯示已提前
終止：兩個實跑 run 的 token 帳以 $15 重建與帳單各差 8.15%／3.71%（既知
儀器殘差量級），以 $10 重建差 37.4%／34.4%——每個變體下 $15 都遠更吻合。
有到期日的牌價格自此以**到期日或帳單證據，先到者為準**判定；判定用比較
擬合（候選費率何者遠更吻合），不用絕對吻合（既知殘差會誤報）。

## 換算錨表（doctrine「the brake」anchors 項的 CC 綁定）

錨值只住本節。變更走 ADR 0003 的 default-change governance。

| class | 錨率（chars per tok-eq） |
|---|---|
| prose | 4 |
| code | 3 |
| cjk | 1.5 |
| 修正係數 | ×1.3 |

- **計算**：`scripts/estimate-tokens.py --anchors prose=4,code=3,cjk=1.5,correction=1.3 <file>...`
  （副檔名→class 規則內嵌於該腳本；CJK 字元逐字入 cjk 桶）。
- **`basis.class` 宣告**：tok 值取工具實算；`class` 是稽核 band 用的粗類，由
  commander 判——單類檔照副檔名、CJK 過半 → `cjk`、跨類合併 → `mixed`。
- **W 估計**：實作類 W ≈ code 錨 × 預估行數 × 平均行寬（~60 chars/行）。
- **稽核**：`scripts/audit-brake-lines.py <journal> --anchors <同上>`。

## Instrumentation switch（doctrine RT-9 的 CC 綁定）

謂詞住 L1；本節只答「那個開關在 CC 上是什麼」。

| | |
|---|---|
| 載體 | `<project-root>/.conductor-instrumented`（在 `.conductor/` 之外——開關必須先於它授權的那棵樹存在） |
| 具體測試 | `[ -f <path> ]`（型別測試、不開檔，落在 L1 規定的行為上） |
| writer | 操作者或 harness |

switch-path: `.conductor-instrumented`
（機械可讀宣告；`scripts/check-instrumentation-switch.sh` 讀它組出載體集合。）

```bash
touch .conductor-instrumented     # 開
rm -f .conductor-instrumented     # 關（預設）
```

跑本 mode 的專案要把這條路徑加進自己的 `.gitignore`；conductor repo 已含。

`[unverified]` 操作者忘了開，量測就靜靜不發生，直到有人發現沒有 journal。
落日條件 FT-p3-3。

## Boot 探針（doctrine「the brake」C_fresh 項的 CC 綁定）

記錄行落 `<project-root>/.conductor/probe.jsonl`（project-local、gitignored；
schema = `contract/probe.schema.json`；唯一 writer = 本程序）。

- **程序**：專案根目錄執行
  `claude -p "Reply with exactly: ok" --model claude-haiku-4-5-20251001 --output-format json`，
  取 JSON `usage` 的 `input_tokens + cache_creation_input_tokens` 為 `boot_tokens`。
- **config_hash**：兩個輸入以 `|` 連接取 sha256 前 12 hex——(1) tier 表全部解析後
  model id，字典序、逗號連接；(2) 本節最後變更日期（YYYY-MM-DD）。現行值：
  ```
  printf 'claude-fable-5,claude-haiku-4-5-20251001,claude-opus-4-8,claude-sonnet-5|2026-07-18' | shasum -a 256 | cut -c1-12
  ```
  model 集合換代或本節版本變動＝hash 變＝確定性重探。連續 `reprobed` ≥3 → deviation。
- **選行**：`scripts/probe-select.py .conductor/probe.jsonl --harness claude-code --config-hash <hex> --model-gen <gen>`
  → `HIT` ｜ `REPROBE` ｜ `ERROR`。

## model_gen 正規化

現行 gen-tag：**`g2026.07`**。上表三 tier 的模型集合不變＝同一 tag；任一 tier
換主版本＝ tag 換新（`gYYYY.MM`，取換代當月）。minor 漂移不換。

## Offered surfaces（journal 的合法量測源）

1. `in-channel-worker-usage` — Agent tool 頻道內回報的 worker token 用量，原樣
   記入 `dispatch_result.usage`；
2. `headless-json` — headless 執行的 JSON 輸出（run 總量；boot 探針即用此面）；
3. `journal-estimate` — commander 對 brief／re-read 體積的 tok-eq 計算
   （`brief_tokens_est`／`reread_tokens_est`）。

session transcript 與 on-disk 內部格式非法源。

## Role card 綁定（doctrine RT-4 @ role-card 的 CC 面）

三張 L2 卡（`contract/roles/`）各對應一個先鑄 agent 定義（`agents/<role>.md`，
由卡值生成：model←tier 本表解析、tools←capability_surface，動詞映射
read→Read、search→Grep+Glob、edit→Edit+Write、run-contracted-*→Bash；戳記與
來源卡同 `graded_under`，任一不符＝agent 檔與卡同時失效）。

使用法：把 `agents/*.md` 安裝到專案 `.claude/agents/`（或經 plugin agents 目錄
載入）後，dispatch 以該 agent type 起 worker；未安裝時回退泛用 agent type ＋
顯式 `model:`。

doctrine_rev 取得：git checkout 用 `scripts/run-obeyed.manifest` 的最後變更
commit；安裝態讀出貨的 `doctrine/REV`。**絕不用 plugin 版號**——版號與卡上
`graded_under` 的 git rev 永不相等，staleness 檢查永遠 miss。REV 新鮮度由
`scripts/check-doctrine-rev.sh` 在 repo 端把關。

## Preventive single-writer enforcement（doctrine RT-6 的 CC 面）

read breadth 一律以唯讀 agent type（`Explore`——工具集無 Write/Edit）派出，宣告
記入 dispatch 記錄的 `read_only` 欄；write worker（`general-purpose`）每個 write
surface 同時至多一個。

**Explore 型 worker 寫不出 result.json**（無 Write 工具，結構性）→ doctrine
「worker report」的 carrier 例外適用：commander 持久化其頻道報告為 task-dir 的
result.json，provenance 註記 commander-persisted。逐字 artifact 要緊時改派
task-dir-scoped 的 write worker。轉錄時 findings 機械逐字；doctrine 詞彙欄位
走 RT-3 @ worker-report——此 harness 的 worker 環境可能帶與本 mode 無關的
工具，誤標風險即該行在這裡的著力點。
