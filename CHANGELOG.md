# Changelog (append-only; every entry traces to a commit)

## Unreleased
- Working onedir build: `dist/Interval/Interval.exe` (194 files, 32.8 MB),
  `optimize=1`, single-instance lock, pruned AVIF/non-win binaries
  (`1b7c37c`, `7128cc1`).
- Measured boot: ~3.8 s to the real window; ~107 MB main + ~121 MB
  renderer. RAM is WebView2-dominated; onedir wins startup, not memory.
- `web/` split: `ui.py` is now a loader over `web/` parts; escape audit
  fixed two real sanitizer/path backslash bugs (`2c57697`).
- Backend splits: `timelib.py`, `store.py` (OTL-aware, traversal guard,
  rotating log, lossless legacy migration), `export_xlsx.py` (`cd08839`).
- Interval rebrand (display strings; repo/code identity stays
  OpenTimeLogger; keystore service string frozen) (`561f321`).
- Benchmark harness `scripts/bench.py` + records (`f016468`).

## Agent graph (T3 hybrid)
- P1 substrate: change detection, parts, assigner, evidence index,
  verifier, scheduler, metering (`f492d72`).
- P2 task graph: timelines, challenges, step linker, refiner
  (user-edits-win), proposer + critic, trajectory DPO (`a3f7c07`).
- P3 coach: pattern DB, LLM-free confounder checker, divider, style
  critic, verbatim-claim narrator, EOD 23:30 (`18fa97e`).

## Platform
- OS keyring for BYOK secrets (ctypes, no new deps), config sanitizing,
  validation, secret scrubbing (`341a42f`).
- Live provider catalog + 4D pricing + cost estimator/spend summary
  (`8640407`).
- Evidenced ASR allowlist from live leaderboard crawl; fail-closed gate
  (`8b44893`). Note: zero models currently verify — selection stays
  closed until ID mappings are confirmed.
- UI wiring: scheduler tick, deep-coach card, cost strip, catalog
  re-scan, evidenced ASR list, preview harness (`4ebfb2f`).
- Open Design strict flow: 4 surfaces generated, saved, screenshotted,
  reviewed; TechHR briefing; routing rule (design = Muse Spark 1.3)
  (`d912677`, `5e7a996`, `abb1db7`, `2a75c98`, `d6678c5`, `7c067b6`).
- 12 repo subagents + T3 spec; models/modes/permissions pinned
  (`ac1ba22`, `88282ba`).
- Frozen cartography + review decisions (`b303ab6`).

## Earlier
- Frameless host, dashboard, AI bridge, onedir spec (`53c55ef`).
- Analytics engine, BYOK layer, mic capture (`0a8c4b4`).
- Frameless titlebar, dashboard, AI workspace UI (`3ded9b5`).
- Seedream 5 logo/icon/avatar (`7011cec`); Interval glass redesign
  (`347a5e9`); localStorage crash fix (`73cfb75`).
