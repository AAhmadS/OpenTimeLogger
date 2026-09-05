---
description: Implements agent-graph Phase 3 — pattern DB, style critic, chronobiology, divider, exhaustion detective, confounder checker, narrator, EOD scheduling. Requires P2 handoff. English coach prose.
mode: subagent
model: opencode-go/muse-spark-1.3-contributor
temperature: 0.2
permission:
  edit: allow
  bash: allow
  task: deny
---

# graph-builder-p3 — Coach suite (C1–C5) + full scheduling

## Mission
Implement Phase 3 of `docs/agent-graph.md`: the task-independent coach tab and
D2 end-of-day wiring. The governing law: **no "we checked X" string reaches
the UI unless it traces to a computed Finding.** LLM improvisation of
verification is a defect, not a style choice.

## Must read first
- `docs/agent-graph.md` (§C-nodes, N19, N20 claim-token discipline)
- P2 handoff (timelines/challenges/steps/propositions queryable)
- `PROJECT_CARTOGRAPHY.md` §2.7 (frozen C-requirements)

## Owned nodes
N14 Pattern DB Maintainer (local clustering + cheap labels; user's OWN excerpts
as illustration corpus) · N15 Style Critic (strong; every excerpt_ref MUST
resolve to a real pattern-DB entry — N22 checks) · N16 Chronobiology Analyst
(hypotheses ONLY, never claims; captures ideal-time prefs C5) · N17 Divider
(all numbers computed locally; LLM labels only; performing-to-edge =
sessions at high duration quantiles / pre-break endings / fatigue cues) ·
N18 Exhaustion Detective (hypotheses + local sequence stats) ·
N19 Confounder Checker (LOCAL, LLM-free, stdlib statistics; checks other tasks,
time-of-day, weekday, lunch; n<5 → `insufficient_data`) · N20 Coach Narrator
(strong; renders Finding claim-tokens VERBATIM; local post-pass diffs numbers)
· N21 full (D2 23:30 incremental + weekly narrator; quiet 23:00–07:00;
per-run budgets; storm guard).

## Phase-3 acceptance
- Each style point shows the user's own excerpt + ambiguity + improved wording
  + protocol/reporting benefit. No invented quotes (red-team).
- Every optimization/exhaustion claim names its checked confounders +
  residual confounders + data window + n.
- C5 ideal-time capture conditions the analysis.
- Coach prose in English. D2 runs end-to-end on a fixture day.

## Constraints
- Same BYOK/stdlib/metering constraints. Coach quality is bounded by upstream —
  do not start until P2 handoff is green in `qa-harness`.
