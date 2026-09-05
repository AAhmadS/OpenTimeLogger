# OpenTimeLogger — Project Cartography

> **PROVENANCE.** This document is the persistent cartography of OpenTimeLogger's
> roadmap and requirements. The main body below is **frozen** — it may never be
> edited. New knowledge is appended to the **Appendices** at the end. Any change
> to a requirement is recorded as a new appendix entry, never as a body edit.

---

## 0. Mission (frozen)

A private, local-first desktop time tracker. Every session stays on disk. The app
must measure the user's work, show them where their time goes, and — with their
own API keys — let an agentic AI pipeline reason over that history.

---

## 1. Product identity (frozen)

- **Name:** OpenTimeLogger (in-app title currently "Interval" — rebrand pending).
- **Tagline:** "time, accounted for".
- **Audience:** a solo builder/engineer who logs daily and nightly work sessions,
  wants analytics, and is building toward AI-assisted self-analysis.
- **Platform:** Windows desktop. Language: English UI (future: Persian).
- **Current stack:** Python 3.11 + pywebview (WebView2) + openpyxl, one-file
  PyInstaller build. Data: `sessions.json` + `exports/*.xlsx`.
- **Current brand:** green accent (#5ec27f) glass-morphism, dark/light themes,
  generated avatar + icon (WaveSpeed Seedream 5-lite).

---

## 2. Frozen requirements

### 2.1 UI/UX modernization
- Check icons and UI with the Playwright MCP; make everything modern and
  standards-compliant. Replace anything that looks 2000s-era.
- **Custom top bar:** the native window title bar must be replaced with a
  customized, themed title bar (frameless window) — the current default chrome
  "shouts old app".
- Design direction is derived from existing material (glass, green accent,
  dark/light), committed without asking the user to arbitrate aesthetics.

### 2.2 Logo
- Exactly **one** WaveSpeed generation for the new app logo, **Seedream 5** only.
  The prompt must be accurate in every sense — no do-overs.

### 2.3 App weight / runtime
- The current build reportedly uses Electron (fact-check: repo is pywebview).
  Research the current best options for lightweight desktop shells
  (pywebview vs Tauri vs Neutralino vs Electron updates) and adopt the most
  efficient path; report the outcome.
- Goal: run the app far more efficiently; smaller/faster binary, lower memory.

### 2.4 Analytics dashboard (static — no LLM needed)
Reference implementation exists at `C:\Users\USER\.vscode\TechHR` (Vue3 + Chart.js
+ Tailwind dashboard; see its `src/components/dashboard/` and screenshots).

Required metrics:
- How many times the user logged **daily vs nightly** sessions.
- **Trend** of performance: weekly, daily, monthly.
- Per **category**, and when a category is clicked (within its tab) the same
  breakdown per **sub-category**.
- **Documentation/work ratio** and its trend weekly and monthly.
- **When**: time-of-day and day-of-week heat — in what time of the day and on
  what weekday the user puts effort into which categories.
- All of the above computable statically from `sessions.json`.

### 2.5 AI / agentic layer (BYOK — only with user-supplied keys)
Design the agent graph and tools; the user sees the whole agentic workflow as an
animated edge-by-edge loading motion, and supplies an API key + provider per
agent. Providers to support: **Mistral AI, OpenRouter, OpenAI API, Avalai,
Google AI Studio.**

Per-agent onboarding flow:
- First agent: user picks provider + key.
- Subsequent agents: proposed default (provider + key from previous), user may
  reuse, change per-agent, or add. Multiple keys per provider supported.
- On provider select: quick scan of provider docs → complete list of capable
  models for that agent's task → user picks, or types a custom model name
  (at their own responsibility).
- Loading animation while model list loads (no dead air).
- **Test-model button** before moving to the next agent: verifies accessibility.
- Runtime failure handling: model becomes inaccessible → visible error →
  options: (a) stop AI for now (halts whole pipeline), (b) repair (another model),
  (c) best preference: same model on other providers → if none, pick from the
  agent's proposed model set by **minimum Euclidean distance in price** to the
  previous model, first available wins → if still none: error with halt/repair only.
- User can change any agent's LLM at any time. Settings view = a scrollable graph
  (vertical, horizontal if needed).
- If the user consents, proposition data + surrounding context is collected into a
  dataset suitable for **DPO preference optimization** of the pipeline (server-side,
  consent-gated).

### 2.6 AI task page (agent-generated structure)
AI reads the session logs and builds a task/subtask structure, filled into a
template:
- **Timeline** per task: e.g. user says "auditing, building, phase 1, mvp, QA" →
  Research & Mockup → Phase 1: MVP → Phase 1: QA → (model improvises from user
  descriptions/notes) Phase 2: Improve UI → …; user can feedback/edit every step.
- **Challenges** per task: each with severity level and status — identified /
  solved / partially solved (partially-solved is clickable: what's done, what's
  remaining).
- **Steps** per task: clicking a timeline state shows its challenges on one side
  and the step timeline on the other; clicking a step re-filters challenges to
  what that step addressed.
- **Step ↔ timelog mapping is many-to-many**: a step is composed of parts of
  multiple timelogs; user can see which parts of which timelogs contributed to a
  challenge's solved-status.
- **Propositions** per step: AI may propose (only when confidently grounded in
  the descriptions) common thinking issues, mind-obscuration, or domain help.
  Each proposition can be checked in/out; saved. Consent-gated data collection.

### 2.7 AI task-independent tab (coach)
Reads logs and proposes:
- Better **logging style** — with examples from the user's own past logs (pattern
  DB of previous logs), showing how a given entry caused ambiguity and how it
  would improve protocol writing / future reporting.
- **Work-time optimization** — e.g. "you are better active at XXXX times/days",
  "you perform better on task X on Monday but not Saturday; checked: not caused by
  other tasks", "when Y is half/totally done, you are ~2x more focused on X".
- **Time-division breakdown** — e.g. 25% coding, 37% reading/research (half PDFs,
  third Chrome tabs); whether the user performs to their edge.
- **Exhaustion/blocking pattern detection** — e.g. "75% of the time after
  managerial work/meetings you either rush a poorly documented coding session or
  wait 2h (you're a 30-min person) — we checked time-of-day and weekday, not
  lunchtime; reorder X", or "X after Y causes Z to be exhaustively done and you
  penetrate into night".
- User is **asked** whether they want to specify ideal time-of-day / day-of-week /
  work hours to improve analysis quality.

### 2.8 ASR (dictation)
- English ASR for dictating descriptions/notes instead of typing.
- User chooses the transcription model — **restricted** to models with
  **< 4% WER** on https://artificialanalysis.ai/speech-to-text/non-streaming.
- English only (documented). On provider select: check which models are available;
  unavailable ones have their selection disabled.

---

## 3. Frozen architecture decisions

- `sessions.json` remains the source of truth; app stays local-first.
- All AI features are **BYOK and opt-in**; no AI call happens without a key.
- The analytics dashboard is computed client-side (or via a thin local API) from
  the same session data; no new cloud dependency.
- Consent-gated DPO dataset collection is a separate server; local app only
  prepares/offers rows.

---

## 4. Execution log (append-only)

### 2026-09-04 — Kickoff
- Project inspected: `session_logger.py` (backend + pywebview host), `ui.py`
  (entire UI as an HTML string), `brand.py` (avatar data URI), PyInstaller spec.
- **Fact check:** the app is **already pywebview-based, not Electron**
  (README + `session_logger.py:759`). "Electron heaviness" concern is moot;
  remaining efficiency work = build packaging + runtime tuning (see §2.3).
- Open Design daemon started at `http://127.0.0.1:7456` (v0.16.1) — it was down,
  now running.
- Requirements §2.1–§2.8 persisted above (frozen body).
- Todo list created (logo → UI audit → research → redesign → dashboard → AI).

<!-- APPENDICES -->

## Appendix A — 2026-09-04 build session (implementation log)

### A.1 Fact checks
- The app was **already pywebview-based, not Electron** (README + `session_logger.py`).
  A research subagent compared Tauri v2 / Neutralino / pywebview / Flutter / .NET /
  Electron-2026: on Windows every webview shell uses WebView2, so RAM is
  WebView2-dominated regardless of shell. **Verdict kept: pywebview.** Applied:
  onefile → **onedir** spec, backend excludes (cef/qt/gtk/cocoa/mshtml), UPX off,
  `optimize=2`. `frameless=True` + `DRAG_REGION_SELECTOR=.titlebar` custom titlebar.

### A.2 Logo (one WaveSpeed shot, Seedream 5)
- Model `bytedance/seedream-v5.0-pro`, 1:1, 2k, PNG. First attempt aborted
  client-side (no prediction created, verified via `wavespeed history`); the
  single counted generation succeeded in 84 s.
- Output: `assets/logo_seedream5.png` (interval-arc + glow mark on navy).
  Derived: `app.ico` (multi-size), `assets/avatar.png` + `brand.py` data URI.

### A.3 New modules
- `analytics.py` — stdlib-only `compute_dashboard(range)` (today/7d/30d/90d/all):
  overview, daily/nightly + buckets, daily/weekly/monthly trends, categories +
  sub-tags + per-category daily trend, doc-ratio weekly/monthly trend, 24×7
  heatmap (+ per-category heatmaps), duration histogram, weekday/hour pattern.
- `ai.py` — BYOK: 5 providers (openai/openrouter/mistral/avalai/google),
  `ai_config.json` key store, chat/test/list-models, price-distance fallback,
  3-agent pipeline (session-analyzer → task-builder → coach) on a background
  thread with pollable status, tasks/insights/reports JSON, proposition toggles,
  consent-gated DPO export, OpenAI-compatible audio transcription.
- `audio_capture.py` — sounddevice 16 kHz mono WAV recorder (base64) for dictation.
- `session_logger.py` — frameless window, `dashboard_stats`, full AI bridge,
  window controls, ASR record/stop/state. Fixed during integration:
  `ai_get_config`→`load_config`, `ai_run_coach(cfg)`, `ai_fallback` resolves the
  agent's stored provider/key/model before calling the 4-arg `fallback_model`.

### A.4 UI (`ui.py` rewritten)
- Custom frameless titlebar (logo, theme, min/max/close via js_api), emerald
  design tokens, inline Lucide-style icon set, nav (Active/Archive/Dashboard/
  AI/Export), pure-SVG charts (no CDN — app is offline).
- Dashboard: KPI grid, day/night split + buckets, trend (daily/weekly/monthly),
  category drilldown with per-category trend, doc-ratio trend, heatmap with
  category filter, duration + rhythm panels, sidebar quick facts.
- AI: onboarding wizard (provider → key → model+test gate per agent, proposed
  defaults carried over), animated agent graph, Tasks (timeline/challenges/
  steps/propositions), Coach (+ideal-hours nudge), Session reports, Pipeline
  with per-agent error box (Use best fallback / Repair model), AI settings modal
  (per-agent LLM change, ASR config with WER-gated models, ideal hours,
  consent + DPO export), mic dictation modal.
- QA: Playwright preview harness (`preview.html` + mock API, real analytics +
  canned AI data isolated via `OTL_APP_DIR`); 3 subagent visual-review rounds;
  real-app boot verified (frameless `OpenTimeLogger` window, ~112 MB process).

### A.5 Process notes / gotchas
- PowerShell 5.1 `Get-Content`/`Set-Content` decode UTF-8 files as cp1252 and
  re-encode the mojibake. Non-ASCII repo files must be assembled with explicit
  `[System.IO.File]::ReadAllText(path, UTF8)`. This corrupted ui.py once and
  the preview mock once; both caught via screenshot + byte checks.
- Preview mock persisted `tasks.json` into the repo and stale `preview_data/`
  masked a fix — preview writes now isolated to temp; user-data files
  (`ai_config.json`, `tasks.json`, `insights.json`, `ai_reports.json`,
  `dpo_dataset.jsonl`) added to `.gitignore`.
- Image analysis: user directed that screenshot review go through opencode
  subagents rather than direct OpenRouter calls. Note: this environment's Task
  tool accepts only a worker type (no model selector), so the model cannot be
  pinned from here — reviews were delegated to `brand-analyzer` subagents.
- Incidental: a broad `Stop-Process -Name python` during smoke-test cleanup may
  have killed unrelated Python processes on the machine, including the preview
  HTTP server (restarted afterwards).

## Appendix B — 2026-09-05 review decisions (locked)

### B.1 Request-vs-implementation gaps (accepted as repair backlog)
- Coach "we checked X" claims are prompt-level only — no computed confounder
  checks behind them (overclaim risk). Fix: local Confounder Checker node;
  every such claim must trace to a computed check, n<5 → `insufficient_data`.
- Model catalog is hardcoded, not a live provider-docs scan. Fix: per-provider
  live-scan protocols with cache + staleness badge (see B.3).
- No pattern DB behind logging-style advice. Fix: Pattern DB Maintainer node
  fed by the user's own excerpts.
- ASR allowlist unevidenced. Fix: Playwright crawl of the
  artificialanalysis.ai STT non-streaming leaderboard (WER<4%, English),
  snapshot + CSV under `docs/asr-evidence/`, monthly refresh.
- Efficiency work unmeasured. Fix: benchmark harness (cold start, working
  set, dist size) before/after any runtime claim.
- Open Design: project `opentimelogger-settings` was scaffolded (brand
  instructions present) but 0 files generated. Strict per-surface project +
  human hand-verification gates adopted going forward.
- Subagent model pinning (Muse Spark 1.3-xhigh / DeepSeek V4 Flash Vision-max /
  mimo v2.5) is not expressible — the Task tool exposes no model parameter.
  Delegation continues by worker type; model choice is environment-side.

### B.2 Locked decisions
- Brand lineage: Seedream 5 only. Superseded `assets/icon_interval*.png`,
  `assets/gen_icon.*`, `wavespeed-output/` deleted, not committed.
- Secrets: `security-auditor` migrates API keys to OS keyring (Windows
  Credential Locker); `ai_config.json` becomes a migration source, not storage.
- Scheduler defaults: end-of-day 23:30, quiet hours 23:00–07:00 (queued jobs
  run at 07:00). D3 debounce 10 min, materiality filter, storm guard.
- Spend: NO in-app cap. Provider-side limits are the guardrail; onboarding
  shows a heads-up to set them. Pricing store is 4-dimensional per model
  (input/output/cache-read/cache-write); Run Log meters every call → per-agent
  + total inferred spend in Settings; daily estimate starts norm-based, then
  usage-based. Shown pre-backfill ("D1 will cost ≈ $X").
- Coach language: English (pattern DB + narrator).
- DPO rows: correct pairs PLUS full flow trajectory (trigger → extractor →
  timeline/challenge/step states → proposition → critique → decision, with
  run/version IDs), frozen at decision time, append-only.
- Agent graph: T3 hybrid (local scheduler + staged mini-DAGs over a versioned
  claim store). Build order P1 (parts/reports/evidence + D3) → P2
  (timeline/challenges/steps/propositions + Refiner + DPO) → P3 (coach +
  Pattern DB + EOD). Old 3-agent path kept behind a flag until P2 lands.
- Skills: `ui-ux-pro-max` installed globally (full); `design-system`
  references only (token architecture); `brand`/`ui-styling`/`slides`/
  `banner-design` skipped (fixed brand / stack mismatch / unneeded).
- Subagents live in `OpenTimeLogger/.opencode/agents/` (10 definitions,
  see Appendix C).

### B.3 Provider live-scan protocols (owned by `provider-scanner`)
- OpenAI: `GET /v1/models` with user key (authoritative) + docs cross-check.
- OpenRouter: keyless `GET /api/v1/models`, modality/architecture filter.
- Mistral: `GET /v1/models` with key + Playwright docs backup.
- Google AI Studio: `GET /v1beta/models?key=`, `supportedGenerationMethods`
  must contain `generateContent` (mechanically documents the no-ASR rule).
- AvalAI: OpenAI-compatible `/v1/models` + Playwright docs backup.
- Catalog = `models_cache.json` {models, capabilities, pricing-4D,
  fetched_at, source}; stale cache → visibly-marked curated seed fallback.

## Appendix C — subagent roster (definitions in `.opencode/agents/`)
- Build crew: `backend-hardener`, `ui-architect`, `graph-builder-p1`,
  `graph-builder-p2`, `graph-builder-p3`, `provider-scanner`, `asr-librarian`,
  `qa-harness`, `visual-reviewer`.
- Governance: `security-auditor`, `release-engineer`, `docs-keeper`.
- (One file per agent; `graph-builder-p*` share the T3 spec, phased.)

### B.4 Subagent model mapping (locked 2026-09-05)
- opencode agent frontmatter supports `model: provider/id` + `temperature` +
  `permission` + `mode` — there is NO `variant` key, and neither
  "Muse Spark 1.3 xhigh" nor "DeepSeek V4 Flash Vision Exp max" exists as a
  model ID in this setup (verified against global agents + opencode docs).
- Mapping used: code/intelligence agents →
  `opencode-go/muse-spark-1.3-contributor` (the Muse Spark 1.3 family member
  actually present); pixel-reading agents (`visual-reviewer`, `asr-librarian`)
  → `opencode-go/mimo-v2.5` (matches global pixel-reader precedent +
  the earlier explicit mimo order); `docs-keeper` → `opencode-go/deepseek-v4-flash`.
- Pixel readers run on Muse Spark 1.3 (`visual-reviewer` switched off mimo
  per user-locked design/front-end routing rule: open-design and all
  design/front-end work use Muse Spark 1.3 via opencode-go or openrouter,
  never mimo v2.5). `asr-librarian` stays on mimo v2.5 (pure data crawl,
  not design) unless ruled otherwise.
- If the provider publishes the exact requested IDs later, it is a one-line
  `model:` change per file.

### B.5 Known issues for the repair phase (found 2026-09-05, not yet fixed)
- `session_logger.py` ignores `OTL_APP_DIR` (only `ai.py` honors it): Store,
  DATA_FILE and exports always resolve to the repo/exe dir. Preview harness
  served real `sessions.json` because of this. Owner: `backend-hardener`
  (unify on one `app_dir()` in `timelib`/`store` split).
- `ui.py` is a non-raw Python string: JS `\n` escapes silently become real
  newlines at import (broke the AI tab at runtime once, caught by preview).
  Owner: `ui-architect` (the `web/` split eliminates the hazard class).

### B.6 Product name correction (2026-09-05, user ruling)
- The app's name is **Interval**. "OpenTimeLogger" remains the repo / code /
  file identity (spec, exe, module docstrings updated cosmetically) and the
  frozen keystore service string (renaming orphans stored keys — see
  `keystore.py`). Frozen §1 body left untouched per the provenance rule.
- Open Design project + token specimen retitled to Interval.

### B.7 Open Design strict flow outcomes (2026-09-05, fully automated)
- Project `opentimelogger-redesign` ("Interval Redesign — strict surfaces"):
  token-specimen.html, dashboard.html (v2), ai-workspace.html,
  onboarding.html — all saved in-project, all screenshotted to
  `docs/od-evidence/`, all self-reviewed (visual-reviewer discipline).
- Review verdicts: tokens PASS; dashboard v1 FAIL (collapsed trend/bar row,
  oversized heat cells) → v2 PASS (fixed heights); AI workspace PASS with
  two vocabulary fixes applied at save (statuses → schema vocabulary,
  finding gained claim text); onboarding PASS with provider chips corrected
  to our 5 BYOK providers at save.
- Generation reliability: ~40% of calls return empty/truncated; retry (and
  splitting oversized briefs) recovers. Never save a truncated artifact —
  verify closing tags before `od_save_project_file`.
- Skill override: ui-ux-pro-max suggested blue/amber OLED; overridden by the
  locked emerald glass brand. Kept: KPI-first ops layout, density-high,
  checklist as QA gate.
- Routing rule: design/front-end work uses Muse Spark 1.3 (opencode-go or
  openrouter), never mimo v2.5 (`visual-reviewer` switched).

### B.8 Build outcomes (2026-09-05, measured)
- Onedir from the tracked spec: 195 files / 42.0 MB (vs stale onefile
  32.6 MB single exe — deleted). Cold start to visible window ~1.3–9 s
  (first-run WebView2 profile creation is the slow end); main process peak
  ~50–113 MB + ~130 MB WebView2 renderer child. RAM is WebView2-dominated
  either way — onedir wins startup (no TEMP extraction), not memory.
- Frozen-boot saga (all in-build, all fixed): (1) exit-1 from
  `optimize=2` stripping docstrings → pycparser can't build → clr_loader →
  pythonnet CLR init fails: spec now `optimize=1`. (2) Concurrent frozen
  boots race CLR init and crash: `store.single_instance()` lockfile guard,
  second copy exits 0 quietly (verified on the built exe). (3) Excluding
  winforms breaks pywebview import — don't. edgechromium-first with
  winforms fallback kept.
- Prune candidates for later: PIL `_avif` codec (7.7 MB, openpyxl doesn't
  need it), `pywebview-android.jar`, non-win portaudio binaries.
  Build deps: pyinstaller + pyinstaller-hooks-contrib (README).

### B.9 web/ split outcomes (2026-09-05)
- `ui.py` (giant string) → `web/` parts (shell_top, styles.css, head.js,
  body.html, app.js, shell_tail); `ui.py` is now a 60-line loader (source
  dir or frozen `_MEIPASS`, shipped via spec datas). Verified by
  `tests/test_web_split.py` + preview render + gui-boot (3.3 s, 121 MB).
- Escape audit (old runtime vs raw file bytes): exactly 4 divergence sites.
  The raw files are CORRECT in all four — the old build was silently
  mangling two of them: filename sanitizer and path-split regexes lost the
  backslash (real Windows-path bugs, now fixed); `\n` string escapes were
  accidentally-correct via double processing. Pinned in tests with
  zero-ambiguity `chr(92)` assertions.
- Loader rule going forward: web/ bytes are served raw — JS string escapes
  SINGLE backslash, regex literal backslashes DOUBLE. Never reintroduce
  Python-string wrapping of frontend code.
