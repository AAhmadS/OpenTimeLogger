# OpenTimeLogger — Agent Graph Spec (T3 hybrid)

Locked decision (Appendix B.2): **orchestrator + staged mini-DAGs over a
versioned claim store**. Local-first, BYOK-only, stdlib Python, budget-aware.
Replaces the linear session-analyzer → task-builder → coach pipeline (kept
behind a config flag until P2 lands).

Hard invariants:
1. No "we checked X" string reaches the UI unless it traces to a computed
   Finding (N19 is the only claim emitter).
2. User edits always win — AI proposes into `proposed`, never overwrites.
3. No LLM call without a user key. Fallback = halt / repair / best-preference
   (price proximity). No in-app spend cap; provider-side limits + onboarding
   heads-up + metered estimates instead.
4. Refinement always terminates (evidence scoping + epoch caps + fixed-point
   detection + cooldowns + storm guard).
5. Cheap/fast models do ~80%; strong/reasoning reserved for improvisation,
   proposition quality, and prose. All LLM outputs schema-bound JSON.

## 1. Node catalog (condensed)

| ID | Node | Class | Emits |
|----|------|-------|-------|
| N1 | Provider Gate | any (probe) | key/model validation, `ready_for_backfill`, price table |
| N2 | Change Detector | local | ChangeSet {added/edited/deleted, materiality} |
| N3 | Part Splitter | local (+cheap assist) | parts[] (first-class timelog segments, stable IDs) |
| N4 | Session Extractor | cheap (strong on low-confidence) | SessionReport: topic, explicit+implicit Qs (`inferred`), steps, numeric + qualitative |
| N5 | Task Assigner | cheap + rules | TaskMembership {task_id, session_ids, confidence} |
| N6 | Timeline Architect | **strong** | phases, `ai_improvised` flagged + evidence-linked |
| N7 | Challenge Miner | cheap (strong on ambiguity) | challenges: severity, status, done[] + remains[] for partial |
| N8 | Step Linker | cheap + local constraints | steps (many-to-many part links) + step↔challenge links |
| N9 | Evidence Indexer | local | entity→(session,part,span,hash); challenge→parts→timelogs map |
| N10 | Proposition Proposer | **strong** | propositions w/ confidence + grounding_refs (abstain-over-guess) |
| N11 | Proposition Critic | **strong**, ideally other provider | pass/reject/soften + reason (mechanical confidence gate) |
| N12 | Refiner / Revision Engine | local (+cheap summaries) | patch vs revise plan; enforces user-wins + termination |
| N13 | DPO Row Builder | local | append-only JSONL: pair + FULL trajectory + frozen context |
| N14 | Pattern DB Maintainer | local + cheap | pattern shapes w/ user's own excerpts + improved wording |
| N15 | Style Critic | **strong** | style points; every excerpt_ref must resolve (N22 checks) |
| N16 | Chronobiology Analyst | cheap | HYPOTHESES only + ideal-time capture (C5) |
| N17 | Divider | local + cheap labels | division shares, sub-splits, edge metrics (computed) |
| N18 | Exhaustion Detective | cheap + local stats | pattern hypotheses + operationalizations |
| N19 | Confounder Checker | **local, LLM-free** | Findings: claim, effect, confounders_checked[], n, window; n<5 → insufficient_data |
| N20 | Coach Narrator | **strong** | renders Finding tokens VERBATIM; local numeric post-pass |
| N21 | Scheduler / Orchestrator | local | trigger→subgraph dispatch, debounce, quiet hours, budgets |
| N22 | Schema Verifier | local | pass/fail + repair hints; no-claim-without-evidence gate |
| N23 | Run Log | local | per-run audit + token/cost metering (feeds cost UI) |

## 2. Triggers (locked defaults)

- **D1 keys-provisioned** → full-history backfill, batched (~20 sessions), once,
  resumable; pre-run cost estimate shown ("D1 will cost ≈ $X").
- **D2 end-of-day 23:30** → incremental extract + scoped refine + numeric
  recompute; narrator re-renders weekly (configurable).
- **D3 session added/edited** → N2 → extract → scoped refine; debounce 10 min,
  coalesce window, materiality filter (metadata-only ≠ structural).
- Manual "Analyze now" (user override, budget shown); model switch (no
  auto-run, `--force` offered); weekly deep revision (1/week max).
- Quiet hours 23:00–07:00: D2/D3 landing inside queue for 07:00.

## 3. Refinement semantics (N12)

Write discipline (learned 2026-09-05, two bugs): never mutate an in-memory
store across a `revise_entity` call — it saves per call, so any earlier
handle is stale. Always fresh-load → mutate → save in one sequence.

- **Patch** (evidence-only: refresh refs+hash, no version bump) vs **revision**
  (structural: new version + supersede chain).
- Entity envelope: `{id, type, version, supersedes[], superseded_by, status
  (active|superseded|proposed|user_authoritative), created_by, ai_improvised,
  user_feedback, evidence_refs[], last_evidence_hash, updated_at}`.
- User edit → `user_authoritative`; AI output → `proposed` (max 1 pending).
- Termination: evidence-scoped refresh (hash intersection) · epoch cap 2/trigger
  · fixed-point detection (refs-only diff → patch+stop) · 30-min entity cooldown
  · 5 refinements/day · storm guard (>20% structural churn → halt-soft + ask).
- Proposition IN/OUT → N13 appends row, **no back-edge into analysis**.

## 4. Stores

`sessions.json` (unchanged) · `sessions_audit.jsonl` · `snapshots/` ·
`session_reports.json` · `tasks.json` (memberships→templates) ·
`evidence_index.json` · `findings.json` (run-scoped) · `patterns.json` ·
`revisions.json` (version ledger) · `user_edits.json` · `dpo_rows.jsonl`
(append-only) · `run_log.jsonl` (metering) · `config.json` (model map, quiet
hours, budgets display, lunch heuristic) · `models_cache.json` (see B.3).

## 5. DPO row shape

`{context: {task_id, phase, step_id, step_goal, proposition, alternatives[],
critique, excerpts[]}, chosen, rejected, trajectory[]: [{node, input_ref,
output_ref, version}], source_run_id, decision: in|out, consent_batch}`.
IN → chosen=proposition; OUT → rejected=proposition (`NO_PROPOSITION` fills
the empty side). Context frozen at decision time.

## 6. Failure semantics

Retry 2× backoff → repair w/ N22 hint → escalate cheap→strong (twice-failed) →
best-preference provider by price proximity → branch-halt with `quality=
degraded` recorded, or halt-soft prompt. Local nodes emit `insufficient_data`,
never fabricate. Scheduler resumes idempotently from run_log.

## 7. Build order

- **P1** (`graph-builder-p1`): N1, N2, N3, N4, N5, N9, N22, N23, N21-minimal.
  Delivers requirement A + working D3 loop + metering.
- **P2** (`graph-builder-p2`): N6, N7, N8, N12, N10, N11, N13. Delivers B1–B4.
- **P3** (`graph-builder-p3`): N14, N15, N16, N18, N17, N19, N20, C5, N21-full.
  Delivers C1–C5 + D2.
