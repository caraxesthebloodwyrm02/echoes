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
- Routines: routines/Glimpse.py; workflows/macro.py
- Prompts: templates/prompts.json; caching/prompt_engine.py

Training & Evaluation
- JSON datasets added: `data/podcasts/lex_musk.json`, `data/podcasts/jre_trump.json`.
- Training uses seeded priors and learned pause thresholds derived from label means.
- Prediction falls back to priors if thresholds are unavailable.

Tests
- `tests/test_pause.py`: seeds/priors and JSON-based threshold predictions.
- `tests/test_workflows_macro.py`: macro parallel + merge contract.
- `tests/test_prompt_cache.py`: cosine similarity and cache ranking.

Next
<<<<<<< Updated upstream
- Add tests in tests/test_pause.py for key semantic pause scenarios.
- Evaluate with synthetic and real timestamped segments.
=======
- Expand datasets and labels; target ≥80% accuracy on annotated events.
- Integrate with STS pipeline for live pause-driven decisions.



>>>>>>> Stashed changes
