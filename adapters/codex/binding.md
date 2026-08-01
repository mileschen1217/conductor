# Capability-tier binding — Codex

L1 names mechanisms; this file holds the values. 查證日期 **2026-07-10**
（`codex --version` 0.142.5；`~/.codex/models_cache.json` fetched 2026-07-09）。

| 能力階層 | 模型 | reasoning effort | 適用任務形 |
|---|---|---|---|
| frontier | `gpt-5.5` | `high`/`xhigh` | 首次診斷、架構取捨、高風險審查 |
| mid | `gpt-5.4` | `medium` | 規格清楚的實作、搜尋、研究 |
| cheap | `gpt-5.4-mini` | `low` | 已解模式批次套用、機械枚舉 |

reasoning effort 無獨立旗標，經 `-c model_reasoning_effort=<level>` 覆寫。
`codex-auto-review` 為 CLI 內部用途，非派工模型，不入表。

## Worker tier（doctrine § Defaults「worker tier」的 codex 綁定）

commander `gpt-5.5` → worker `gpt-5.4` 為預設。

**`gpt-5.4-mini` 作 worker 的准入——三條件全中才合法**：(1) brief 純機械、零殘留
判斷；(2) 有便宜的可執行 check artifact；(3) 小而多的子任務，單次重派成本有界。

`[unverified]` 本 binding 無費率表，故三條件是可移植的**風險**判準（失敗要機器
抓得到、重派成本要有界），不是成本結論。cheap-tier 作 worker 樣本數 0。

## 缺值：r 表、換算錨表、boot 探針（doctrine「the brake」r/anchors/C_fresh 項的 codex 面）

**本 binding 三者皆無。** Codex 無公開 token 成本係數，粗比例無誠實取值基礎。

後果只落在 instrumented run 的計算面：economics leg 不可計算 → brake
`verdict=not-computable`，offload 僅四項 necessity ground 可派（doctrine
RT-2），缺值記入 deviation log。ordinary run 的 brake 本就是質性判斷，故本 binding 在
ordinary run 上與其他 binding 同等可用。

## Instrumentation switch（doctrine RT-9 的 codex 綁定）

謂詞住 L1；本節只答載體。與 CC binding 同一條路徑：一個專案只有一個「這輪要不要
量」的答案，開關屬於量測場合而非 harness。

| | |
|---|---|
| 載體 | `<project-root>/.conductor-instrumented`（在 `.conductor/` 之外） |
| 具體測試 | `[ -f <path> ]` |
| writer | 操作者或 harness |

switch-path: `.conductor-instrumented`

```bash
touch .conductor-instrumented     # 開
rm -f .conductor-instrumented     # 關（預設）
```

跑本 mode 的專案要把這條路徑加進自己的 `.gitignore`。

## model_gen 正規化

現行 gen-tag：**`g2026.07`**。規則同 CC binding：tier 表任一模型換主版本＝tag
換新（`gYYYY.MM`）；minor 漂移不換。

## Role card 綁定（doctrine RT-4 @ role-card 的 codex 面）

sandbox flag 由卡的 `capability_surface.read_only` 機械映射；AGENTS.md fragment
貼入 worker workspace（承本 adapter README「AGENTS.md load fragment」，外加該卡
職責一行）。戳記失效規則與 rev 來源同 CC binding。

| 卡 | sandbox flag | model | AGENTS.md fragment 附加行 |
|---|---|---|---|
| read-scout | `--sandbox read-only` | `gpt-5.4` | `Role card: contract/roles/read-scout.md — read-only; findings cited file:line, delivered in the result summary.` |
| mech-writer | `--sandbox workspace-write` | `gpt-5.4-mini` | `Role card: contract/roles/mech-writer.md — recipe application inside Owned Files only; record every contracted command's exit code.` |
| fresh-verifier | `--sandbox read-only` | `gpt-5.4` | `Role card: contract/roles/fresh-verifier.md — fresh context, no builder state; per-criterion pass/fail with file:line evidence.` |
