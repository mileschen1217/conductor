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

## 價格比 r 與單位權重（doctrine § Amortization brake 的 codex 綁定）

**本 binding 目前無 r 表**：Codex 無公開 token 成本係數（上節成本備註、
spec deferred D-1），粗比例無誠實取值基礎。依 doctrine § Amortization
brake 的 cold-start 規則：economics leg 不可計算 → fan-out 經濟面
conservative-closed，僅必要理由（wall-clock／corpus／disjoint-write）可派，
缺值記入 deviation log。benchmark 實測產生費率證據後回填本節（變更記
changelog）。

changelog：
- 2026-07-16 建節，記缺值（v3 build）。

## model_gen 正規化

現行 gen-tag：**`g2026.07`**（gpt-5.5 世代，models_cache fetched
2026-07-09）。規則同 CC binding：tier 表任一模型換主版本＝tag 換新
（`gYYYY.MM`）；minor 漂移不換。

## User-level 常數表

路徑與 schema 同 mode 慣例：`~/.codex/conductor/constants.jsonl`（operator-
local，不 ship，起始為空），行 schema = `contract/constants.schema.json`。
**本 binding 尚無 collector**：offered surface 待盤點（codex exec 的 JSON
輸出面）；在那之前 codex-side run 的常數一律 UNVERIFIABLE 行（手記或缺）。

## Role card 綁定（doctrine § Complexity tiering — Role cards 的 codex 面）

三張 L2 卡（`contract/roles/`）的 codex 配方——sandbox flag 由卡的
`capability_surface.read_only` 機械映射；AGENTS.md fragment 貼入 worker
workspace（承本 adapter README §「AGENTS.md load fragment (worker side)」
的既有配方，外加該卡職責一行引用）。戳記失效規則同 CC：卡 `graded_under` 與現行 doctrine rev／
gen-tag 任一不符＝配方同卡失效。

| 卡 | sandbox flag | model（tier 本表解析） | AGENTS.md fragment 附加行 |
|---|---|---|---|
| read-scout | `--sandbox read-only` | `gpt-5.4`（mid） | `Role card: contract/roles/read-scout.md — read-only; findings cited file:line, delivered in the result summary.` |
| mech-writer | `--sandbox workspace-write` | `gpt-5.4-mini`（cheap） | `Role card: contract/roles/mech-writer.md — recipe application inside Owned Files only; record every contracted command's exit code.` |
| fresh-verifier | `--sandbox read-only` | `gpt-5.4`（mid） | `Role card: contract/roles/fresh-verifier.md — fresh context, no builder state; per-criterion pass/fail with file:line evidence.` |

## Advisor transport（doctrine § Advisor primitive 的 codex 綁定）

digest 封套：commander 把該判斷時刻的完整 context 濃縮為 digest 檔
（`<task-dir>/advisor/<moment_id>-digest.md`），以 frontier 檔次呼叫：

    codex exec --sandbox read-only -m gpt-5.5 \
      "You are an advisor to an orchestration commander. Read the digest
       below and return EXACTLY one JSON object (no prose) with fields:
       decision_type, ruling, rationale, confidence (high|medium|low),
       what_would_change_my_mind.
       --- DIGEST ---
       $(cat "$task_dir/advisor/${moment_id}-digest.md")" < /dev/null

回傳 JSON 填 `digest_ref` 後即 `advisor_ruling` 行 payload（schema:
`$conductor/contract/advisor-ruling.schema.json`）。與 CC 側差異＝傳輸形
（digest 上行 vs full-context 上行）；可移植性保證只及 schema 層，ruling
內容 parity 明文不保證（spec REQ-8）。

### worker→advisor 面（doctrine § Advisor primitive 的 codex 綁定）

codex worker 跑在獨立 sandbox，其工具面不含本 mode 的 advisor primitive，故
worker→advisor 路徑**推定不存在**——但這是**推理，非實測**（CC 側正是在此處推錯
過一次：把 session 級缺席讀成 worker 級隔離）。因此：

- **Observation surface：無。** undisclosed-use 檢查在 codex 側常態＝
  **UNVERIFIABLE，永不 CLEAN**，直到有 probe 為止。治理同 CC：靠契約宣告
  （task-contract § Advisor Scope）+ worker 揭露義務。
- Measurement-bearing run（benchmark cell／parity／ablation）若含 codex 臂，
  該臂的 tier 宣稱以 UNVERIFIABLE 記錄，不得記為 CLEAN——見
  `benchmark/protocol.md` § Isolation invariants 第 5 條。
