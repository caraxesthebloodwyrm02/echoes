install:
\tcd backend && poetry install
\tcd frontend && npm install

dev:
\t# run backend and frontend concurrently (example)
\tcd backend && poetry run uvicorn app:app --reload

test:
\tcd backend && poetry run pytest
