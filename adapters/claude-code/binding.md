# Capability-tier binding — Claude Code

查得方法：Agent tool `model` 參數合法值（sonnet | opus | haiku）+ Claude Code
官方文件的現行模型 ID（操作者本機的 dispatch 慣例檔可覆寫此表）。
查證日期：2026-07-10。

| 能力階層 | 模型/agent | 適用任務形 | 備註 |
|---|---|---|---|
| frontier | opus（`claude-opus-4-8`）；commander 本體通常即主對話模型 | 首次診斷、架構取捨、跨檔不變量、高風險審查第二意見 | 判斷不外包；commander 自任 frontier 時不另派 |
| mid | sonnet（`claude-sonnet-4-6`）— Agent tool 預設工人；唯讀 fan-out 用 `Explore` agent type | 規格清楚的實作、搜尋/盤點、多源研究、審查 lens | 預設工人 |
| cheap | haiku（`claude-haiku-4-5-20251001`） | 已解模式批次套用、格式轉換、機械枚舉 | 紅線：需判斷/首次遇到/配方含糊不給 cheap |

Preventive single-writer enforcement（REQ-6 SHALL 的 CC 面）：平行 fan-out
worker 一律以唯讀 agent type（`Explore`——工具集無 Write/Edit）派出，且該宣告
記入該次 run 的 dispatch 記錄（single-writer 稽核的配置證據）；寫入型 worker
（general-purpose）同時至多一個。
