# ECHO Project Memory

## Identity and purpose

ECHO means Attack Chain Reconstruction Engine. It is a research-oriented application that reconstructs probable attack chains from imperfect security events, explains supporting and contradicting evidence, represents uncertainty, and evaluates predictions against independent ground truth. It must be more than a log viewer.

## Working environment

- Windows, Visual Studio Code, and Claude Code.
- The developer is a beginner in Python, so future explanations should be simple while code remains maintainable.
- The workspace is `C:\Users\Vidhi Desai\Documents\ECHO`.

## Approved stack and introduction order

- Python core engine first, with pytest for tests.
- FastAPI only when the API is authorized in Master Prompt 3.
- PostgreSQL only when persistence is authorized in Master Prompt 3.
- React investigation interface only when authorized in Master Prompt 3.
- Docker when justified during integration and release work.
- Do not add machine learning without a justified research design.

## Approved UI direction

A future dark digital-forensics workspace with a persistent left sidebar, cyan/electric-blue accents, and five screens: Investigation Dashboard, Attack Graph Explorer, Event Timeline, Evidence Inspector, and Research & Experiments. No frontend is implemented in Master Prompt 1.

## Research principles

- Keep observed evidence, normalized records, inferred relationships, hypotheses, and ground truth distinct.
- The prediction path must not receive expected relationship labels.
- Preserve provenance and uncertainty; do not confuse chronological order, correlation, inference, and causation.
- Use synthetic events first and preserve experiment configurations and random seeds.
- Prefer reproducible metrics over unsupported claims.

## Security principles

- Treat imported records as untrusted data, never executable content.
- Preserve original evidence and record transformations.
- Never log passwords, reusable tokens, raw recovery codes, or secret credentials.
- Use default-deny authorization and tenant isolation controls when SaaS functionality is introduced.
- Do not mark controls complete without evidence.

## Repository conventions

- Source code is under `src/echo/`; tests are under `tests/`; design documents are under `docs/`.
- Use `pyproject.toml`, pytest, type hints where useful, and small focused modules.
- Use ASCII by default and do not commit secrets, local environments, caches, or generated experiment output.

## Verified state after Master Prompt 3

- The workspace was empty before setup; no existing files, Git repository, or ECHO implementation required preservation.
- Python 3.14.3 is available through `py`; `python` and global `pytest` were not available on PATH during inspection.
- Created `README.md`, `pyproject.toml`, `.gitignore`, `docs/SecurityChecklist.md`, `docs/Architecture.md`, `docs/memory.md`, `src/echo/__init__.py`, `src/echo/cli.py`, and `tests/unit/test_cli.py`.
- Created `src/echo/__main__.py` after validating the documented `python -m echo` command.
- Created `.venv` locally and installed the editable project with pytest 8.4.2; `.venv` is ignored by Git.
- Implemented `models.py`, `ingestion.py`, `scenarios/generator.py`, `reconstruction.py`, `graph.py`, `evaluator.py`, and the expanded CLI.
- Added deterministic synthetic degradation, event-time candidate generation, evidence explanations, graph serialization, incremental updates, and CLI integration tests.
- Added measured evaluation metrics, FastAPI routes, Pydantic request validation, SQLAlchemy PostgreSQL models, migration SQL, `.env.example`, and a React/Vite dashboard with five API-connected screens.
- Installed backend and frontend dependencies locally. PostgreSQL client/server and Docker are unavailable, so live database connectivity and migration execution are unverified.
- Fixed live integration issues found during final browser validation: explicit `localhost`/`127.0.0.1` CORS support, accessible investigation creation form, real dashboard synthetic import action, selectable graph nodes/timeline events, and idempotent repeated event imports.

## Unresolved decisions

- Broader event-type coverage, calibrated uncertainty if justified, graph-version persistence, and full experiment metrics remain for future work.
- Authentication, authorization, rate limiting, live PostgreSQL verification, deployment, retention, and multi-tenant behavior remain future scope.

## Four-master-prompt workflow

1. Foundation, documentation, and runnable core setup.
2. Complete reconstruction engine and imperfect-evidence handling.
3. Evaluation, API, and React investigation dashboard.
4. Integration, security validation, testing, and release.

## Current next action

Proceed to Master Prompt 4 for integration, security validation, browser checks, and release preparation.

## Validation record

- CLI: verified with `.venv\\Scripts\\python.exe -m echo`, `generate`, `import`, and `reconstruct`; the final degraded run generated 8 observed records, reconstructed 7 nodes and 7 edges, and repeated graph exports had identical SHA-256 hashes.
- Tests: verified with `.venv\\Scripts\\python.exe -m pytest`; 16 tests passed, with one Starlette/httpx deprecation warning.
- Compilation: verified with `.venv\\Scripts\\python.exe -m compileall -q src tests`.
- API: verified with FastAPI TestClient for health/version, investigations, event validation, reconstruction, timeline, evidence, experiments, metrics, and safe malformed input handling using the explicit memory fallback. SQLAlchemy PostgreSQL models/configuration exist, but API repository wiring and live connectivity remain unverified.
- Frontend: `npm run typecheck` and `npm run build` both passed; Vite produced `frontend/dist`.
- PostgreSQL: not verified; `psql` and Docker were unavailable in the environment.
- Browser: verified live at `127.0.0.1:5173` with the fallback API: create investigation, generate 7 events, reconstruct 5 edges, repeat generation without duplicate growth, select graph node, select timeline event, inspect evidence, and run an experiment. Desktop and 390px viewport checks passed; browser console had zero errors.
- Secret scan: completed; no configured common secret patterns were found in project files.
- Dependency installation: verified; editable install and pytest 8.4.2 succeeded under Python 3.14.3.
