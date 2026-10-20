# ECHO

ECHO (Attack Chain Reconstruction Engine) is a research-oriented Python project for reconstructing probable attack chains from incomplete, delayed, duplicated, noisy, and out-of-order security events. It is designed to make relationships explainable and measurable rather than acting as a simple log viewer.

## Current prototype

Master Prompts 1 and 2 now provide the documented foundation and a working local reconstruction core:

- A documented architecture, security checklist, and project memory.
- Typed and timezone-normalized event validation with original payload preservation.
- Deterministic synthetic scenarios with separately stored ground truth and configurable degradation.
- Safe JSON ingestion with invalid-record reports and duplicate flags.
- Bounded event-time candidate generation, explainable rule-based evidence scoring, and uncertainty labels.
- Deterministic directed graph serialization, rejected candidates, and incremental late-event updates.
- A pytest suite covering the core and CLI.

Master Prompt 3 adds a FastAPI API, SQLAlchemy/PostgreSQL schema and migration, measured evaluation, and a React/TypeScript dashboard. PostgreSQL connectivity is not verified because `psql` and Docker are unavailable; without `DATABASE_URL`, the API uses an explicitly labeled in-memory development fallback. Authentication, deployment hardening, and scientific benchmark claims remain out of scope.

## Prerequisites

- Windows PowerShell.
- Python 3.11 or newer. The foundation was validated with Python 3.14.3 through the `py` launcher.
- Internet access only when installing the test dependency from the package index.
- Node.js and npm for the dashboard.
- PostgreSQL for persistent mode. It is not installed or verified in the current environment.

## Setup in PowerShell

From the repository root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

If PowerShell blocks activation, use the venv interpreter directly or follow your organization's execution-policy guidance:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

## Run ECHO

With the virtual environment active:

```powershell
python -m echo
```

The package currently exposes the same entry point through:

```powershell
echo
```

The no-argument CLI reports project identity; the commands below exercise the implemented Master Prompt 2 core.

Generate a deterministic synthetic scenario:

```powershell
python -m echo generate --output .\scenario.json --seed 17 --delayed-rate 1 --duplicate-rate 0.25
```

Validate imported events:

```powershell
python -m echo import --input .\scenario.json
```

Reconstruct and export a graph:

```powershell
python -m echo reconstruct --input .\scenario.json --output .\graph.json
```

The generated JSON contains ground truth for later evaluation, but the reconstruction command removes it from its graph output and does not pass it to prediction code.

## Run the API

The SQLAlchemy PostgreSQL configuration path is prepared, but it has not been connected to a live database in this environment. Copy `.env.example` to `.env` and replace only local placeholder values for future verification. Without `DATABASE_URL`, the API explicitly reports `memory-development-fallback`; with it, the API reports `postgresql-configured-unverified` until the database repository wiring is validated.

```powershell
Copy-Item .env.example .env
$env:DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@localhost:5432/echo"
python -m uvicorn echo.api:app --reload --port 8000
```

## Run the dashboard

In a second PowerShell window:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dashboard contains the five connected views: Investigation Dashboard, Attack Graph Explorer, Event Timeline, Evidence Inspector, and Research & Experiments.

## Run tests

```powershell
python -m pytest
```

Frontend checks:

```powershell
Set-Location frontend
npm run typecheck
npm run build
```

The PostgreSQL schema is in `migrations/001_initial.sql` and has not been executed against a live database in this environment. With PostgreSQL installed and a dedicated `echo` database created, apply it from PowerShell with `psql "$env:DATABASE_URL" -f .\migrations\001_initial.sql`, then start the API with the same `DATABASE_URL`. The current API reports `postgresql-configured-unverified` until this connection and repository wiring have been tested.

## Documentation

- [Architecture](docs/Architecture.md)
- [Security checklist](docs/SecurityChecklist.md)
- [Project memory](docs/memory.md)

## Planned delivery workflow

The project uses four master prompts: foundation and documentation, reconstruction engine and imperfect evidence, evaluation/API/dashboard, then integration/security validation/release. This repository is verified through Master Prompt 3; Master Prompt 4 remains for integration, security validation, browser checks, and release preparation.
