## Speech Module: Pause Interpretation and Routines

Scope
- Semantically aware pause metrics for speech-to-speech (STS) interactions.
- Reusable routines (10-step) and parallel macro workflow (big/medium/fast/polish layers).
- Prompt templates with scoring and caching for chaining across contexts.

Design Principles
- Seeded, reproducible experiments; Windows-friendly commands.
- Data ethics: public podcast transcripts only; cite sources.
- Modularity: no regressions to existing simulations or CI.

Artifacts
- Data: data/podcasts/*.json (transcripts, timestamps, pause annotations)
- Model: speech/pause_model.py (training/eval scaffold)
- Routines: routines/engine.py; workflows/macro.py
- Prompts: templates/prompts.json; caching/prompt_engine.py

Next
- Add tests in tests/test_pause.py for key semantic pause scenarios.
- Evaluate with synthetic and real timestamped segments.
