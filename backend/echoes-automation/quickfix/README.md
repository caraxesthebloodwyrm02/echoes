# Echoes QuickFix Backend Service

This module exposes the `/quickfix` endpoint and integrates with the Lumina agent to propose and return actionable fixes.

## Structure

- `quickfix_app.py`: FastAPI entrypoint defining the REST interface.
- `lumina_client.py`: Wrapper for invoking Lumina tasks and provider models.
- `models.py`: Pydantic schemas for requests and responses.
- `tests/`: Unit and integration tests (pytest).

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn quickfix_app:app --reload
```

## Environment Variables

- `LUMINA_API_KEY`: Credential for Lumina agent interactions.
- `QUICKFIX_ALLOWED_KEYS`: Comma-delimited list of allowed `x-api-key` values.
