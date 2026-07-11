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

## Advisor transport（doctrine § Advisor primitive 的 CC 綁定）

- 傳輸 = CC 內建 advisor tool。前置：人一次性 `/advisor <model>`（session 級
  配置，commander 無法自行配置）。未掛/pairing 不合法 → doctrine 的
  `advisor_unavailable` 降級路徑。
- **Per-call digest 紀錄（本 binding 的必填義務；L2 schema 的 `digest_ref`
  在 CC 側必填）**：呼叫前把送審 context 的 digest 寫到
  `<task-dir>/advisor/<moment_id>-digest.md`，`advisor_ruling` 行的
  `digest_ref` 指向它——full-context call 旁的獨立見證，跨 binding 比對用。
- **Per-worker advisor opt-out：不存在**（probe 1，下）。advisor 是 session
  級的：配對合法時它同時出現在 commander 與**每一個 worker**的工具面，
  commander 無法只給自己不給工人。故 worker→advisor 只能以**契約宣告
  （task-contract § Advisor Scope）+ 事後偵測**治理，絕不可假設「工人沒有
  那個工具」。
- Observation surface（`audit-judgment-flow.py --advisor-observations` 的
  producer）：**已驗證存在**（probe 2，下）。producer =
  `adapters/claude-code/advisor-observations.py`（transcript → observations.jsonl）。
  未跑 producer 時 undisclosed-use 檢查 UNVERIFIABLE，不報 CLEAN。

### Probe 紀錄（2026-07-12 實測；目的＝觀測非 enforcement）

- **probe 1（per-worker advisor opt-out）：CLOSED — 無 opt-out。**
  兩次實測分屬兩種 session 狀態，差異的成因是**配對合法性**，不是 worker 隔離：
  - fable 主 session（`advisorModel: opus` 已在 settings 中）：worker
    （Explore）工具面無 advisor——但主線程**也**沒有。fable 主僅收 fable
    advisor（見上表 pairing 限制）→ 配對非法 → advisor 整個 session 不掛。
    當時誤讀為「CC 無 worker→advisor 路徑」，是把 session 級缺席看成 worker
    級隔離。
  - opus 主 session（同一 `advisorModel: opus`）：配對合法 → advisor 出現在
    主線程，**且傳播到 worker**（Explore worker 前置載入 `advisor`，實測呼叫
    成功）。
  推論：advisor 的有無由 session 級配對決定，worker 一律繼承。**沒有任何
  per-worker 開關。**
- **probe 2（advisor 呼叫可觀測性）：CLOSED — 有觀測面，且涵蓋 worker。**
  - CC 把 advisor 呼叫記為 caller transcript 裡的 `server_tool_use`
    （`{"type":"server_tool_use","name":"advisor"}`），**主 session 與 subagent
    transcript 皆然**；該筆記錄另帶 top-level `advisorModel`、subagent 側帶
    `agentId`。worker 的 advisor 呼叫**留得下痕跡**——undisclosed use 可偵測。
  - hook 面不是產出面：advisor 是 server-side tool，PreToolUse/PostToolUse
    的 matcher 面向 client tool；本 binding 不依賴 hook。
  - OTel（`claude_code.cost.usage`）**無** advisor 專屬列——不要拿 telemetry
    當觀測面。
  - Producer（runnable，有 fixture 套件）：
    `adapters/claude-code/advisor-observations.py`
    ＋ `adapters/claude-code/test-advisor-observations.sh`（11 cases）。
    join 是間接的：subagent 的 `meta.json` 只有 `toolUseId`，沒有 task_id，故
    `server_tool_use → meta.toolUseId → 主 transcript 的 Agent tool_use →
    其 prompt 的 marker 行`。
  - **Commander 的硬性義務（CC 面）：每一次 dispatch 的 prompt 必須含一行
    `Task contract: <task_id>`**（錨定整行比對；子字串比對會讓「順口提到別的
    task」的 prompt 偷走歸戶，把真的 undisclosed use 變成別人的乾淨紀錄）。
    無 marker 的 dispatch 其 advisor 使用**不可稽核**。
  - **Fail-closed 的實現方式＝不產檔，不是產一個壞檔**：任何一筆 advisor 呼叫
    歸不了戶（無 marker／marker 指向未宣告的 task／多重 marker／`spawnDepth>1`
    ／缺 meta／transcript 壞行／content 形變／缺 `subagents/` 目錄），producer
    **stdout 一行不寫**並非零退出。沒有 observations 檔 → audit 的 undisclosed-use
    檢查回報 UNVERIFIABLE（絕不 CLEAN）。**部分產出比不產出更危險——它看起來像
    「沒有呼叫」的證據。**
  - L2 側同時補上兩道防禦（皆由 codex 審查實跑抓出，本 binding 原本的
    fail-closed 宣稱是空的）：observations 含**任何 result 未宣告的 task_id**
    → UNVERIFIABLE（「記在無人認領的 id 底下」不再是藏身處）；帶
    `--advisor-observations` 卻**沒帶 `--results`** → UNVERIFIABLE（記帳的另一
    邊不在，什麼都清不掉）。此前兩者都靜默回 CLEAN。
  - **未證的一格**：以上證明 worker **能**呼叫且呼叫**可見**；worker 是否會
    **自發**呼叫（無 prompt 指示）未測——而 undisclosed-use 正是針對自發呼叫。
    觀測面已就位，此格由實跑累積，不由 probe 斷言。

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
