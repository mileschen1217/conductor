# Capability-tier binding — Claude Code

查得方法：Agent tool `model` 參數合法值（sonnet | opus | haiku | fable）+
Claude Code 官方文件的現行模型 ID（操作者本機 dispatch 慣例檔可覆寫此表）。
查證與釘文件日期：**2026-07-11**。官方 advisor 頁與 subagents 頁互不引用
（單向性）＝FT-v2-5 訊號：行為可能無聲變動，本表大改前回訪官方文件。

| 能力階層 | 模型/agent | 適用任務形 | 備註 |
|---|---|---|---|
| frontier | fable（`claude-fable-5`）；opus（`claude-opus-4-8`）為次選 | 首次診斷、架構取捨、跨檔不變量、advisor 位 | advisor pairing 限制：fable 主對話僅接受 fable advisor（sonnet 主 → opus advisor 合法） |
| mid | sonnet（`claude-sonnet-5`）— Agent tool 預設工人；唯讀 fan-out 用 `Explore` agent type | 規格清楚的實作、搜尋/盤點、多源研究、審查 lens | 預設工人；v1 表載 claude-sonnet-4-6 已過期（telemetry 實證 claude-sonnet-5，2026-07-10 benchmark） |
| cheap | haiku（`claude-haiku-4-5-20251001`） | 已解模式批次套用、格式轉換、機械枚舉 | 紅線承 doctrine § Capability tiers |

tier-0 不入表：tier-0 是 script（Bash/Python），不經 Agent tool。

## 價格比 r 與單位權重（doctrine § Amortization brake 的 CC 綁定）

**Per-pair 列，非 tier 粒度**：frontier tier 內部有 2× 價差（fable output
$50 vs opus $25，官方 pricing 頁實查 2026-07-17），tier 級單一 r 對 opus
commander 會高估省項一倍。r = worker output 牌價 ÷ commander output 牌價。

| r[worker←cmd] | fable cmd（$50/Mtok out） | opus cmd（$25） | sonnet cmd（$10, intro） |
|---|---|---|---|
| worker = sonnet（$10） | 0.2 | 0.4 | 1.0 |
| worker = haiku（$5） | 0.1 | 0.2 | 0.5 |

同 model r=1.0 是定義（doctrine § Amortization brake）；表中對角線的
1.0 僅為一眼可讀而列出，非牌價推導。

單位權重（token 種類換算成 output-token 等值；官方牌價結構比在各 model
內部一致：input:output = 1:5、5m cache-write = 1.25×input）：
`weight[output]=1, weight[cache-write]=0.25, weight[input]=0.2`

changelog：
- **2026-07-17 per-pair 修正（miles 質疑觸發，官方 pricing 頁實查）**：
  fable≠opus（2×），原 frontier 折疊列作廢；r[mid←opus] 0.2→0.4、
  r[cheap←mid] 0.3→0.5、r[cheap←fable] 0.05→0.1。sonnet 現行為
  introductory pricing（$2/$10，至 2026-08-31）；**排程 re-pin：
  2026-09-01** sonnet 恢復 $3/$15 → 全表 sonnet 相關列位移
  （r[sonnet←fable]→0.3、r[haiku←sonnet]→0.33 等）。
- 2026-07-16 初版（v3 build）：跨代結構比推估，已被上列實查值取代。

## model_gen 正規化（constants 表 key 與 role card 戳記用）

現行 gen-tag：**`g2026.07`**。正規化規則：上表三 tier 的現行模型集合不變
＝同一 tag；任一 tier 換代（表列模型 id 更換主版本）＝ tag 換新（格式
`gYYYY.MM`，取換代當月）。minor id 漂移（如 dated snapshot 更新）不換 tag。

## User-level 常數表（doctrine § Precedent & eval loop 的 CC 綁定）

- 路徑：`~/.claude/conductor/constants.jsonl`（operator-local；不 ship；
  安裝起始為空——每 family 起始即 `[pending-measurement]`）。
- 行 schema：`contract/constants.schema.json`（L2 單一 home）。
- Append 一律 flock＋單行 O_APPEND（`tools/collect-run-stats.py` 內建）。
- Offered surfaces（collector 的合法量測源，依 doctrine「介面非內部」）：
  1. `in-channel-worker-usage` — Agent tool 頻道內回報的 worker token 用量，
     commander 原樣記入 journal `dispatch_result.usage`；
  2. `headless-json` — headless 執行的 JSON 輸出（run 總量；帳單級）；
  3. `journal-estimate` — commander 對 brief／re-read 體積的 tok-eq 估計
     （journal additive 欄位 `brief_tokens_est`／`reread_tokens_est`）。
  session transcript／on-disk 內部格式非法源（doctrine 明令）。

## Role card 綁定（doctrine § Complexity tiering — Role cards 的 CC 面）

三張 L2 卡（`contract/roles/`）各對應一個先鑄 agent 定義
（`agents/<role>.md`，由卡值生成：model←tier 本表解析、tools←
capability_surface，動詞映射：read→Read、search→Grep+Glob、edit→
Edit+Write（含 result artifact 的建檔）、run-contracted-*→Bash；
戳記與來源卡同 `graded_under`，任一不符＝agent 檔與卡同時失效）。使用法：把 `agents/*.md` 安裝到專案 `.claude/agents/`
（或經 plugin agents 目錄載入）後，dispatch 以該 agent type 起 worker；
未安裝時回退泛用 agent type＋顯式 `model:` 參數（Phase 3 規則不變）。
doctrine_rev 的取得：`git log -1 --format=%h -- <doctrine 檔路徑>`
（doctrine 檔自身的最後變更 commit，非 repo HEAD——HEAD 隨任意 commit
變動會令卡永遠過期）；**plugin 安裝（無 `.git`）讀出貨的 `doctrine/REV`
戳記檔**——絕不用 plugin 版號：版號與卡上 `graded_under` 的 git rev 永不
相等，staleness 檢查永遠 miss、card 機制靜默失效（v3 回歸實測缺口 1/4）。
REV 新鮮度由 `scripts/check-doctrine-rev.sh` 在 repo 端把關（doctrine 變更
後的 follow-up commit 更新 REV，與卡 re-key 同車）。

## Advisor transport（doctrine § Advisor primitive 的 CC 綁定）

- 傳輸 = CC 內建 advisor tool。前置：人一次性 `/advisor <model>`（session 級
  配置，commander 無法自行配置）。未掛/pairing 不合法 → doctrine 的
  `advisor_unavailable` 降級路徑。
- **Per-call digest 紀錄（本 binding 的必填義務；L2 schema 的 `digest_ref`
  在 CC 側必填）**：呼叫前把送審 context 的 digest 寫到
  `<task-dir>/advisor/<moment_id>-digest.md`，`advisor_ruling` 行的
  `digest_ref` 指向它——full-context call 旁的獨立見證，跨 binding 比對用。
- **Per-worker advisor opt-out：不存在**（probe 1）。advisor 是 session
  級的：配對合法時它同時出現在 commander 與**每一個 worker**的工具面，
  commander 無法只給自己不給工人。故 worker→advisor 必須以**契約宣告
  （task-contract § Advisor Scope）+ worker 自身揭露義務**治理，絕不可假設
  「工人沒有那個工具」。
- **Observation surface：本 binding 不提供。** CC 未對外提供任何 advisor 使用的
  介面級觀測面（probe 2）——唯一留痕處是 session transcript，那是 CC 的
  **內部格式**，doctrine § Advisor primitive 明令 mode 不得綁 harness 內部實作。
  故 CC 側 undisclosed-use 檢查的常態＝**UNVERIFIABLE，永不 CLEAN**；worker→
  advisor 的治理靠**契約宣告**（task-contract § Advisor Scope）+ worker 自身
  揭露義務。**harness 若謊報 worker 的執行事實，那是 harness 的缺陷，不是本
  mode 的威脅模型。**
- Measurement-bearing run（benchmark cell／parity／ablation——輸出「這份工作由
  某 tier 完成」這種宣稱的 run）另有要求：那類 run 的數字會被未揭露的 consult
  無聲汙染，故須一次性查驗。工具與程序在 **`benchmark/`**，不在本 binding：
  `benchmark/tools/cc-advisor-observations.py`（明載綁 CC 內部、升級即可能失效；
  失效時正解是 UNVERIFIABLE 或改由 agent 人工讀，不是往內部鑽更深）。

上兩條陳述（無 per-worker opt-out；無介面級觀測面）的實測依據：
`benchmark/probes/2026-07-12-cc-advisor-probes.md`（probe 1 + probe 2，
均 CLOSED）。本 binding 只承載結論。

## Precedent ledger（doctrine § Precedent & eval loop 的 CC 綁定）

- 路徑：`<project-root>/.conductor/precedent.jsonl`（repo 追蹤檔；歷史不可變
  性由 version control 稽核——既有行改寫在 diff 現形即違規）。
- Promote-pending 通報 channel：`PushNotification` 工具（schema 已驗證存在；
  session 級；使用者在終端時自動略過——skip 即 report-only 降級的天然形）。
  emission 失敗降級 report-only（journal `calibration_notify` 行記
  `status=failed`），絕不擋 run close。

## Preventive single-writer enforcement（doctrine § Single-writer rule 的 CC 面）

read breadth 一律以唯讀 agent type（`Explore`——工具集無 Write/Edit）派出，
宣告記入 dispatch 記錄；write worker（`general-purpose`）每個 write surface
同時至多一個（disjoint-write shape：面不相交、各面單筆、merge 合流單筆）。

Explore 型 worker **寫不出 result.json**（無 Write 工具，結構性）：唯讀契約
的 Expected Output 以頻道內報告為主要交付；commander 將報告逐字持久化為
task-dir 的 result.json（機械轉錄，provenance 註記 commander-persisted）——
write shape 為 inline/1-worker 時不破 single-writer。逐字 artifact 要緊時
改派 task-dir-scoped 的 write worker。（實測：MR9 witness run，4/5 Explore
worker 交付被此擋下；承 sonnet-v2form precedent lesson。）

轉錄界線：findings 內容機械逐字；但 worker 自報的 `judgment_events` 等
doctrine 詞彙欄位須經 commander 自行核判才入 artifact——worker 環境可能帶
與 mode Advisor Scope 無關的 harness 層 advisor 工具，其誤標自報若被盲信
轉錄即污染 ledger（實測：MR9 partition-1 廢稿自報 2 筆禁區
acceptance-interpretation consult，實為環境工具誤標）。
