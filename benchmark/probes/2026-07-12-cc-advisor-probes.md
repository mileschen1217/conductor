# CC advisor probes — 2026-07-12（實測紀錄；目的＝觀測非 enforcement）

支撐 `adapters/claude-code/binding.md` § Advisor transport 的兩條介面陳述
（無 per-worker opt-out；無介面級觀測面）。本檔是證據史料，不是 binding 的
一部分——binding 只承載結論。

## probe 1（per-worker advisor opt-out）：CLOSED — 無 opt-out

兩次實測分屬兩種 session 狀態，差異的成因是**配對合法性**，不是 worker 隔離：

- fable 主 session（`advisorModel: opus` 已在 settings 中）：worker（Explore）
  工具面無 advisor——但主線程**也**沒有。fable 主僅收 fable advisor（binding
  表 pairing 限制）→ 配對非法 → advisor 整個 session 不掛。當時誤讀為「CC 無
  worker→advisor 路徑」，是把 session 級缺席看成 worker 級隔離。
- opus 主 session（同一 `advisorModel: opus`）：配對合法 → advisor 出現在
  主線程，**且傳播到 worker**（Explore worker 前置載入 `advisor`，實測呼叫
  成功）。

推論：advisor 的有無由 session 級配對決定，worker 一律繼承。**沒有任何
per-worker 開關。**這正是 worker→advisor 必須靠契約治理（task-contract
§ Advisor Scope + worker 揭露義務）、而非靠「工人沒有那個工具」的原因。

## probe 2（advisor 呼叫可觀測性）：CLOSED — 介面級觀測面不存在

- **hook 面：無。** advisor 是 server-side tool，PreToolUse/PostToolUse 的
  matcher 面向 client tool。
- **OTel（`claude_code.cost.usage`）：無** advisor 專屬列（16032 列中零命中）。
- **僅存的痕跡在 session transcript**：呼叫記為 `server_tool_use`
  （`{"type":"server_tool_use","name":"advisor"}`），主 session 與 subagent
  transcript 皆然，另帶 `advisorModel`／`agentId`。**但 transcript 是內部
  格式，不是 CC 對外承諾的介面**——依 doctrine（mode 綁介面不綁內部）不得
  作為 binding 的依賴。此發現的正確歸屬是 benchmark 工具
  （`benchmark/tools/cc-advisor-observations.py`），不是 binding。
- **未證的一格**：以上證明 worker **能**呼叫；worker 是否會**自發**呼叫
  （無 prompt 指示）未測——而 undisclosed-use 正是針對自發呼叫。此格由
  measurement-bearing run 的一次性查驗累積，不由 probe 斷言。
