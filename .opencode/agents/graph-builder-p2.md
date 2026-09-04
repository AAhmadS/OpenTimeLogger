---
name: graph-builder-p2
description: Implements agent-graph Phase 2 — timeline, challenges, step linking, refiner, propositions + critic, DPO builder. Requires P1 stores frozen. The highest-interaction surface.
---

# graph-builder-p2 — Task graph (B1–B4)

## Mission
Implement Phase 2 of `docs/agent-graph.md`: the per-task template with
user-editability at EVERY level. This is the surface where the tiniest brief
details matter — implement them literally and acceptance-test against the
brief's B1–B4 examples verbatim.

## Must read first
- `docs/agent-graph.md` (§B-nodes, Refiner semantics, DPO row shape)
- P1 handoff (store schemas, version envelope, evidence index)
- `PROJECT_CARTOGRAPHY.md` §2.6 (frozen B-requirements — the acceptance text)

## Owned nodes
N6 Timeline Architect (strong model; every improvisation flagged
`ai_improvised=true` + evidence-linked) · N7 Challenge Miner (severity +
identified/solved/partially_solved; partially-solved MUST emit done[] AND
remains[]) · N8 Step Linker (many-to-many parts↔steps + step↔challenge links;
local constraint pass) · N12 Refiner/Revision Engine (patch vs revision,
`user_authoritative` always wins, max 1 pending proposal/entity, termination
rules) · N10 Proposition Proposer (strong; abstain-over-guess) ·
N11 Proposition Critic (independent second opinion, mechanical confidence gate)
· N13 DPO Row Builder (pairs + FULL flow trajectory, frozen context,
append-only JSONL, consent-gated).

## Phase-2 acceptance (verbatim from brief)
- Timeline improvisation (e.g. Phase 2 from notes) marked, editable, feedbackable.
- Clicking a timeline state shows challenges one side, step sequence other side;
  clicking a step re-filters challenges to what it addressed.
- Any challenge status resolves to WHICH PARTS of WHICH timelogs contributed.
- Propositions appear ONLY when grounded; IN/OUT persists; DPO rows include the
  full trajectory (trigger → extractor → states → proposition → critique →
  decision + run/version IDs).
- User edits are never silently overwritten (red-team this with `qa-harness`).

## Constraints
- N12 must exist before AI revisions touch anything the user can edit.
- Same BYOK/stdlib/metering constraints as P1. Hand off P3-ready
  (timelines, challenges, steps, propositions queryable by the coach suite).
