# ASR evidence (asr-librarian)

## Snapshot 2026-09-05
- Source: https://artificialanalysis.ai/speech-to-text/non-streaming
- Metric: AA-WER v2 (% words wrong, lower better; 3 datasets incl.
  English AA-AgentTalk/VoxPopuli/Earnings22).
- Raw table: `leaderboard-2026-09-05.csv` (56 rows, extracted from the
  page's summary table via Playwright). Screenshot:
  `asr-leaderboard-2026-09-05.png`.
- Gate (frozen §2.8): strictly **below 4% WER**, English.

## Verdict on the previous allowlist (`whisper-1`, `gpt-4o-transcribe`)
- `whisper-1` → closest benchmarked row "Whisper Large v2, OpenAI" = **4.1%**:
  FAILS the gate on the number; API-ID mapping additionally unverified.
  Status: **suspended-needs-mapping**.
- `gpt-4o-transcribe` → row "GPT-4o Transcribe" = **4.0%**: not strictly
  below 4. Status: **suspended-fails-gate**.
- Row "GPT Transcribe, OpenAI" (3.3%) has no certain API-ID mapping:
  **suspended-needs-mapping** (never guess endpoint IDs).
- Mistral "Voxtral Small" (2.8%) and "Voxtral Mini Transcribe 2" (3.6%)
  pass the number but need exact transcription-endpoint model IDs:
  **suspended-needs-mapping**.
- Google rows (Gemini Transcribe 2.6% etc.) are irrelevant: Google AI
  Studio exposes no English ASR endpoint (mechanical rule stands).

## Policy
Selectable = `verified` rows in `asr_allowlist.json` only. With zero
verified rows the feature gates closed and says why, with this evidence
linked. Refresh monthly; never widen without a fresh snapshot.
