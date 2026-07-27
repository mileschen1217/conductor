# Capability-tier binding — Claude Code

查得方法：Agent tool `model` 參數合法值（sonnet | opus | haiku | fable）+
Claude Code 官方文件的現行模型 ID（操作者本機 dispatch 慣例檔可覆寫此表）。
查證與釘文件日期：**2026-07-11**。官方文件對這些介面的行為可能無聲變動，
本表大改前回訪官方文件。

| 能力階層 | 模型/agent | 適用任務形 | 備註 |
|---|---|---|---|
| frontier | fable（`claude-fable-5`）；opus（`claude-opus-4-8`）為次選 | 首次診斷、架構取捨、跨檔不變量 | 通常即 commander 自身 |
| mid | sonnet（`claude-sonnet-5`）— Agent tool 預設工人；唯讀 fan-out 用 `Explore` agent type | 規格清楚的實作、搜尋/盤點、多源研究、審查 lens | 預設工人；v1 表載 claude-sonnet-4-6 已過期（telemetry 實證 claude-sonnet-5，2026-07-10 benchmark） |
| cheap | haiku（`claude-haiku-4-5-20251001`） | 已解模式批次套用、格式轉換、機械枚舉 | 紅線承 doctrine § Capability tiers |

tier-0 不入表：tier-0 是 script（Bash/Python），不經 Agent tool。

## Worker tier（doctrine § Capability tiers「worker tier default」的 CC 綁定）

L1 的一句原則落到本表：**預設低 commander 一階**（opus commander → sonnet
worker），並取「預期一次 dispatch 就過驗收的最便宜階」。

- **為什麼是一階而不是兩階**：opus→sonnet 已吃下每 token 省項的約 80%；
  sonnet→haiku 只再多約 16 個百分點，但失敗階差大——一次 haiku 失敗＝一次
  sonnet 重派的 C_fresh ＋ 額外 harvest 往返，蓋過那 16%。
- **haiku 作 worker 的准入（三條件全中才合法）**：(1) brief 純機械、零殘留
  判斷；(2) 有便宜的可執行 check artifact，失敗由機器抓而非自報；(3) 小而多
  的子任務，單次重派成本有界、16% 才複利。典型：逐模組盤點/掃描工位、
  測試輸出收集、格式 sweep。
- **誠實線**：haiku-as-worker 在本專案紀錄中樣本數 **0**（M9 測到的崩落是
  haiku 作 *commander*，不同位置）。上列三條件是推理，不是實測結論；首個
  樣本由 MigrationBench 臂帶出，屆時以實測回寫本節並記 changelog。

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

## 換算錨表（doctrine § Amortization brake「conversion anchors」的 CC 綁定）

Brake 的計算輸入（C_brief_cmd／C_brief_worker／C_reread／C_fresh corpus 項）
一律「實物 bytes → tok-eq」換算；錨值只住本節（L1 名機制不載值），變更走
doctrine § Durable records 的 default-change governance（先於文字變更的迴歸
證據，引在改動的 spec/commit 裡）＋本節 changelog——與 r 表同構。
粗比例（數量級精度）；estimate-drift 訊號軌是收斂機制。

| class | 錨率（chars per tok-eq） | 依據 |
|---|---|---|
| prose | 4 | 業界慣用 ~4 chars/tok（英文散文） |
| code | 3 | 程式碼 token 密度較高 |
| cjk | 1.5 | CJK 1–1.8 chars/tok band 取中 |
| 修正係數 | ×1.3 | tokenizer 實測偏高修正（v3.1 assay 研究） |

- **計算工具**：`scripts/estimate-tokens.py --anchors prose=4,code=3,cjk=1.5,correction=1.3 <file>...`
  （tier-0 純算術；錨值全由 CLI 傳入，腳本零內嵌值）。副檔名→class 分類規則
  內嵌於該腳本（code = py/sh/js/ts/json/yaml/toml/…，其餘 = prose；CJK 字元
  按內容逐字入 cjk 桶——混排檔自動分桶，tok 值已含 CJK 貢獻）。
- **brake event 的 `basis.class` 宣告**：tok 值一律取工具實算（上行）；
  `class` 是稽核 band 用的粗類宣告，由 commander 判：單類檔照副檔名
  （prose/code）、CJK 佔比過半 → `cjk`、跨類多檔合併 basis → `mixed`
  （auditor 對 mixed 取三類 band 聯集，doctrine computed-term 稽核容差）。
- **W 估計錨**：實作類 W ≈ code 錨 × 預估行數 × 平均行寬（~60 chars/行級）；
  以人有手感的單位（檔數/行數）估，經同一套錨換算入 brake。
- **稽核**：`scripts/audit-brake-lines.py <journal> --anchors prose=4,code=3,cjk=1.5,correction=1.3`
  以 basis.bytes 重算 band 核對（journal 方言）。

changelog：
- 2026-07-18 promote `cal-anchor-cjk-0001`：CJK 1.5 **re-affirmed**（值不動；
  AC-11 promote-channel paperwork witness，人裁 miles——ledger 零 drift 證據，
  見證對象是通道非量測）。
- 2026-07-18 建節（v3.1 build）：首版值承 assay 研究（prose~4／code~3／
  CJK 1–1.8 取中 1.5／修正 ×1.3）。

## Boot 探針（doctrine § Amortization brake「boot-probe record」的 CC 綁定）

C_fresh 的 boot 項（harness 固定 context-establishment 開銷）由一次性探針
量得，記錄行落 `<project-root>/.conductor/probe.jsonl`（project-local，
gitignored，不 ship；schema = `contract/probe.schema.json`；唯一 writer =
本探針程序，run 量測永不回寫）。

- **程序（cheap-tier 一問一答）**：專案根目錄執行
  `claude -p "Reply with exactly: ok" --model claude-haiku-4-5-20251001 --output-format json`，
  取回傳 JSON `usage` 的 `input_tokens + cache_creation_input_tokens` 為
  `boot_tokens`（首 request 的 context-establishment 總量；量值跨 tier 通用
  ——同一 tokenizer 面）。
- **config_hash 輸入清單（首版，變更記本節 changelog）**——可執行配方，
  兩個具名輸入：(1) tier 表全部解析後 model id，字典序排序、逗號連接；
  (2) 本節 changelog 最新條目日期（YYYY-MM-DD）。兩者以 `|` 連接成 UTF-8
  字串取 sha256（取前 12 hex 作 config_hash）。現行值的計算命令：
  ```
  printf 'claude-fable-5,claude-haiku-4-5-20251001,claude-opus-4-8,claude-sonnet-5|2026-07-18' | shasum -a 256 | cut -c1-12
  ```
  model 集合換代或探針程序版本（=本節 changelog 日期）任一變動＝hash 變
  ＝確定性重探。清單過寬的 thrash 訊號軌：probe event 連續 `reprobed` ≥3
  → deviation（doctrine Error Handling）。
- **選行**：`scripts/probe-select.py .conductor/probe.jsonl --harness claude-code --config-hash <hex> --model-gen <gen>`
  → `HIT`（直接消費）｜`REPROBE`（跑探針、append 新行）｜`ERROR`
  （conservative-closed：brake verdict=not-computable，necessity ground only）。
- **只在 instrumented run 讀寫**（doctrine § Audit surface trigger enum）：
  ordinary run 既不讀探針也不寫探針，其 boot 項不入算。instrumented run 的
  第一次 dispatch 若無可用行才探；entry 永不因探針失敗 block。

changelog：
- 2026-07-18 建節（v3.1 build）：首版程序＋hash 輸入清單（model id 集合＋
  本節版本）。

## model_gen 正規化（role card 戳記與 probe 記錄 key 用）

現行 gen-tag：**`g2026.07`**。正規化規則：上表三 tier 的現行模型集合不變
＝同一 tag；任一 tier 換代（表列模型 id 更換主版本）＝ tag 換新（格式
`gYYYY.MM`，取換代當月）。minor id 漂移（如 dated snapshot 更新）不換 tag。

## Offered surfaces（journal 記錄面的合法量測源）

依 doctrine「介面非內部」：

1. `in-channel-worker-usage` — Agent tool 頻道內回報的 worker token 用量，
   commander 原樣記入 journal `dispatch_result.usage`（typed enum：數值物件
   | `"unavailable"`）；
2. `headless-json` — headless 執行的 JSON 輸出（run 總量；帳單級；boot
   探針即用此面）；
3. `journal-estimate` — commander 對 brief／re-read 體積的 tok-eq 計算
   （journal additive 欄位 `brief_tokens_est`／`reread_tokens_est`，經
   換算錨表）。

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

## Preventive single-writer enforcement（doctrine § Single-writer rule 的 CC 面）

read breadth 一律以唯讀 agent type（`Explore`——工具集無 Write/Edit）派出，
宣告記入 dispatch 記錄的 `read_only` 欄；write worker（`general-purpose`）每個 write surface
同時至多一個（disjoint-write shape：面不相交、各面單筆、merge 合流單筆）。

Explore 型 worker **寫不出 result.json**（無 Write 工具，結構性）：唯讀契約
的 Expected Output 以頻道內報告為主要交付；commander 將報告逐字持久化為
task-dir 的 result.json（機械轉錄，provenance 註記 commander-persisted）——
write shape 為 inline/1-worker 時不破 single-writer。逐字 artifact 要緊時
改派 task-dir-scoped 的 write worker。（實測：MR9 witness run，4/5 Explore
worker 交付被此擋下。）

轉錄界線：findings 內容機械逐字；但 worker 自報的 doctrine 詞彙欄位須經
commander 自行核判才入紀錄——worker 環境可能帶與本 mode 無關的 harness 層
工具，其誤標自報若被盲信轉錄即污染紀錄（實測：MR9 partition-1 廢稿自報 2 筆
禁區 decision_type，實為環境工具誤標）。

**本節的規則不依賴 instrumentation**：唯讀 fan-out 用唯讀 agent type、
write worker 同時至多一個，這兩條在 ordinary run 與 instrumented run 上
一字不差地適用（doctrine § Single-writer rule：預防面是程序不是文書）。
