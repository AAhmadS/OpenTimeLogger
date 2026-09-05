# TechHR dashboard briefing (research agent, 2026-09-05)

Source: `C:\Users\USER\.vscode\TechHR` — Vue3 + Pinia + Chart.js + Tailwind.
9 files in `src/components/dashboard/`, 20 screenshots. Full briefing in
session log; key takeaways for OpenTimeLogger surface 2:

## Copy these
- **KPI strip on top**: title (xs uppercase gray) + 2xl–3xl value + delta
  badge + 16px colored icon. Reports view: totalTime, focusRatio, lateNight%,
  sessions, activeDays, blockers.
- **Late-night rule**: session counts with `hour >= 22 || hour < 6`, amber
  flag at >= 15%. Prefer minute-based variant for our dashboard.
- **Cadence tabs**: Daily/Weekly/Monthly segmented switch; bucket keys:
  daily `YYYY-MM-DD`, weekly Monday-start, monthly `YYYY-MM`.
- **Expandable period rows**: label + n sessions + normalized bar
  (`width = totalMin / maxPeriodMin`, min 4%) + total + ratio% + chevron;
  expanded = category h-bars + sub-category h-bars + entry table.
- **Ranked h-bars**: label + track + fill + `dur · pct%` (universal, pure CSS/SVG).
- **focusRatio pattern** (`deep/(deep+meet)`) generalizes to our
  `docMin/workMin` + progress bar + per-period sparkline.
- **Import row rules** (`services/timesheet.js`): recompute duration from
  start/end, midnight-crossing +24h + flag, forward-fill blank task, skip
  trailing empties, keyword project/activity derivation, blocker regex.
- **Numbers**: tabular-nums, durations as Latin `12h 05m` even in RTL.

## Build new (TechHR has none)
- Time-of-day × weekday × category heat matrix (7 × 4–6 buckets, intensity
  = minutes, optional per-category tint). Only hour extraction + day
  bucketing reusable.

## Explicitly NOT copying
- chart.js/vue-chartjs, Tailwind build, xlsx npm, lucide-vue, SPA
  router/pinia, Vite chain (all incompatible with offline single HTML).
- Client-side cloud AI key (`callMistral` ships `VITE_MISTRAL_API_KEY`).
- localStorage-as-backend; hardcoded mock deltas (+12%/-5%); unscaled
  decorative bars; sidebar SPA chrome; EN/FA i18n system.
- `derivePhase` (text after first `:`) is computed but never displayed in
  TechHR — we WILL display it (sub-category drilldown).
