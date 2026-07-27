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

## Worker tier（doctrine § Capability tiers「worker tier default」的 codex 綁定）

L1 原則：預設低 commander 一階，取「預期一次 dispatch 就過驗收的最便宜階」。
本表的一階梯：commander `gpt-5.5`（frontier）→ worker `gpt-5.4`（mid）為預設。

- **`gpt-5.4-mini`（cheap）作 worker 的准入（三條件全中才合法）**：(1) brief
  純機械、零殘留判斷；(2) 有便宜的可執行 check artifact，失敗由機器抓而非
  自報；(3) 小而多的子任務，單次重派成本有界。典型：逐模組盤點/掃描工位、
  格式 sweep。
- **誠實線**：本 binding 無費率表，故上列「省多少」在 codex 側無數字支撐；
  三條件是可移植的**風險**判準（失敗要機器抓得到、重派成本要有界），不是
  成本結論。cheap-tier 作 worker 在本 adapter 樣本數 0。

## 價格比 r 與單位權重（doctrine § Amortization brake 的 codex 綁定）

**本 binding 目前無 r 表、無換算錨表、無 boot 探針程序**：Codex 無公開
token 成本係數（上節成本備註），粗比例無誠實取值基礎；錨率與探針程序亦
未盤點。此三缺只影響 instrumented run 的**計算面**——ordinary run 的
brake 本就是質性判斷（doctrine § Amortization brake「Two forms, one rule」），
故本 binding 在 ordinary run 上與其他 binding 同等可用。依 doctrine § Amortization brake 的 cold-start
規則（v3.1 觸發條件 = 無探針/無錨）：economics leg 不可計算 → brake
verdict=not-computable，offload 僅必要理由（四項 ground：wall-clock／
corpus／disjoint-write／verification-mandated）可派，缺值記入 deviation log。benchmark 實測產生費率證據
後回填本節（變更記 changelog）。

changelog：
- 2026-07-18 v3.1：cold-start 觸發條件改綁探針/錨缺席（doctrine 同步）；
  明文本 binding 三缺（r 表／錨表／探針）。
- 2026-07-16 建節，記缺值（v3 build）。

## model_gen 正規化

現行 gen-tag：**`g2026.07`**（gpt-5.5 世代，models_cache fetched
2026-07-09）。規則同 CC binding：tier 表任一模型換主版本＝tag 換新
（`gYYYY.MM`）；minor 漂移不換。

## Role card 綁定（doctrine § Complexity tiering — Role cards 的 codex 面）

三張 L2 卡（`contract/roles/`）的 codex 配方——sandbox flag 由卡的
`capability_surface.read_only` 機械映射；AGENTS.md fragment 貼入 worker
workspace（承本 adapter README §「AGENTS.md load fragment (worker side)」
的既有配方，外加該卡職責一行引用）。戳記失效規則同 CC：卡 `graded_under` 與現行 doctrine rev／
gen-tag 任一不符＝配方同卡失效。rev 來源同 CC binding：git checkout 用
doctrine 檔最後變更 commit；安裝態讀出貨的 `doctrine/REV`，絕不用 release
版號（版號對不上卡戳，staleness 永 miss）。

| 卡 | sandbox flag | model（tier 本表解析） | AGENTS.md fragment 附加行 |
|---|---|---|---|
| read-scout | `--sandbox read-only` | `gpt-5.4`（mid） | `Role card: contract/roles/read-scout.md — read-only; findings cited file:line, delivered in the result summary.` |
| mech-writer | `--sandbox workspace-write` | `gpt-5.4-mini`（cheap） | `Role card: contract/roles/mech-writer.md — recipe application inside Owned Files only; record every contracted command's exit code.` |
| fresh-verifier | `--sandbox read-only` | `gpt-5.4`（mid） | `Role card: contract/roles/fresh-verifier.md — fresh context, no builder state; per-criterion pass/fail with file:line evidence.` |
