# Capability-tier binding — Codex

查得方法：`codex --version`（0.142.5，brew）+ `codex exec --help` 確認
`-m/--model` 與 `-s/--sandbox`（`read-only` | `workspace-write` |
`danger-full-access`）+ `~/.codex/config.toml`（本機目前設定
`model = "gpt-5.5"`, `model_reasoning_effort = "medium"`；reasoning effort
無獨立旗標，經 `-c model_reasoning_effort=<level>` 覆寫）+
`~/.codex/models_cache.json`（CLI 快取的完整模型目錄：`slug` /
`display_name` / `description` / `supported_reasoning_levels`，
`fetched_at: 2026-07-09T19:15:48Z`）。目錄列出四筆：`gpt-5.5`、`gpt-5.4`、
`gpt-5.4-mini`（皆 `visibility: list`，可用）、`codex-auto-review`
（`visibility: hide`，內部自動審查用途，非派工模型，本表不採用）。
查證日期：2026-07-10。
成本備註：Codex 無公開 token 成本係數（spec deferred D-1）——本表成本欄為定性
描述，benchmark 實測後回填。

| 能力階層 | 模型/agent | 適用任務形 | 備註 |
|---|---|---|---|
| frontier | `gpt-5.5`，reasoning effort `high`/`xhigh` | 首次診斷、架構取捨、高風險審查 | models_cache 描述："Frontier model for complex coding, research, and real-world work"；亦為 `config.toml` 本機目前設定的預設 model（該檔預設 effort 為 `medium`，此處依任務形升至 `high`/`xhigh`）。定性：最高費率檔 |
| mid | `gpt-5.4`，reasoning effort `medium` | 規格清楚的實作、搜尋、研究 | models_cache 描述："Strong model for everyday coding"；`config.toml` 的 `[notice.model_migrations]` 標示 `gpt-5.4`→`gpt-5.5` 升級建議，但 models_cache 仍列 `gpt-5.4` 為 `visibility: list`（現行可用，非棄用）。定性：中費率檔 |
| cheap | `gpt-5.4-mini`，reasoning effort `low` | 已解模式批次套用、機械枚舉 | models_cache 描述："Small, fast, and cost-efficient model for simpler coding tasks"。定性：最低費率檔 |
