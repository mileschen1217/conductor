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
- Per-worker advisor opt-out：見 probe 紀錄（下）。
- Observation surface（`audit-judgment-flow.py --advisor-observations` 的
  producer 候選 = hook probe）：見 probe 紀錄（下）。無觀測面時
  undisclosed-use 檢查 UNVERIFIABLE，不報 CLEAN。

### Probe 紀錄（2026-07-11 build 期實測；目的＝觀測非 enforcement）

- probe 1（per-worker advisor opt-out）：2026-07-12 實測——advisor 未附掛的
  session 中，read-only worker（Explore）工具面完全無 advisor 形工具
  （loaded + deferred 清單均無）；CC 的 worker→advisor 路徑今日預設不存在，
  「opt-out」問題反轉為「opt-in」。advisor 附掛後是否傳播到 worker 工具面＝
  pending（需 `/advisor` 附掛 session 重跑 probe；一次性人為前置）。
- probe 2（advisor 呼叫 hook 可觀測性）：pending 同一前置（`/advisor` 未附掛
  無從觸發）。在完成前本 binding 無已驗證觀測面——
  `audit-judgment-flow.py` 的 undisclosed-use 檢查於 CC 側現況 =
  UNVERIFIABLE（不報 CLEAN）；probe 完成後回填 `observations.jsonl` 產出
  配方。

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
