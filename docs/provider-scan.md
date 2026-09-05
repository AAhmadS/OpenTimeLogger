# Provider live-scan protocols (provider-scanner)

Primary path is HTTP (`models.scan`, key-gated per Appendix B.3). This
document specifies the **Playwright docs-page backup** for when a list
endpoint fails or returns nothing usable. Polite rules for every protocol:
single pass, 30 s navigation timeout, no login, cache the result, never
block onboarding on a failed scan.

## Common steps
1. `browser_navigate` to the docs URL below; `browser_wait_for` the model
   table/cards to render (JS-heavy pages: wait for table text, not load).
2. `browser_snapshot` → extract model IDs + capability hints (context window,
   "audio input/output", "transcription", "embedding" markers).
3. Screenshot to `docs/provider-evidence/<provider>-<date>.png`.
4. Transcribe into `models_cache.json` with `source: docs-playwright` and the
   snapshot date; mark pricing `null` unless the page states it.

## Per-provider
- **OpenAI** — https://platform.openai.com/docs/models . Table rows carry
  model IDs; capability column distinguishes text / audio / realtime.
  Transcription models (whisper-*, gpt-4o-transcribe) → caps `["asr"]`.
- **OpenRouter** — https://openrouter.ai/models . Cards carry `:online`
  variants and modality tags; the HTTP endpoint already returns pricing, so
  docs backup only fills model presence.
- **Mistral** — https://docs.mistral.ai/getting-started/models/ .
  Model cards list capabilities; Voxtral/transcription entries → `["asr"]`.
- **Google AI Studio** — https://ai.google.dev/gemini-api/docs/models .
  Rule stays mechanical: only models whose docs list text generation count
  as chat; audio-only/transcription endpoints do not satisfy the English-ASR
  gate (that gate belongs to asr-librarian's leaderboard evidence).
- **AvalAI** — https://avalai.ir/models (may require Persian locale render;
  wait for price table). OpenAI-compatible IDs map 1:1; tag `whisper-1` asr.

## Freshness
Cache TTL 7 days (`CACHE_TTL_SECONDS`). UI shows source + fetched_at +
stale badge; stale cache degrades to the labeled seed list, never to
silence.
