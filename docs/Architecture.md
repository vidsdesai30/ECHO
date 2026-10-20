# ECHO Architecture

**Status:** The Python reconstruction core, measured evaluation module, FastAPI local API, SQLAlchemy persistence model, migration SQL, and React dashboard are implemented. PostgreSQL connectivity and unrestricted deployment are not verified.

## 1. Purpose and scope

ECHO is a research-oriented attack chain reconstruction engine. It imports synthetic security events, validates and normalizes them, proposes evidence-supported relationships, builds an attack graph, exposes uncertainty and competing hypotheses, and evaluates reconstruction output against independently defined ground truth. The initial scope is synthetic events and a directly executable Python core. ECHO is not a production SIEM, incident-response authority, or causal proof system.

## 2. Requirements

Functional requirements are ingestion, preservation, validation, normalization, candidate relationship generation, evidence explanation, graph reconstruction, uncertainty representation, incremental updates, ground-truth-isolated evaluation, reproducible metrics, and experiment reports.

Non-functional requirements are deterministic runs when configured with a seed, reproducibility, explainability, safe handling of untrusted input, testability without services, clear provenance, bounded resource use, and beginner-readable code. Performance targets are unresolved until representative synthetic workloads exist.

## 3. Research objectives

The research objective is to study how incomplete, delayed, duplicated, noisy, and out-of-order observations affect reconstruction. Experiments should compare known synthetic ground truth with predictions using pre-declared configurations, random seeds, metrics, and limitations. ECHO must not claim novelty, superior accuracy, or successful outcomes without evidence.

## 4. System boundaries

The core owns synthetic scenario generation, event processing, relationship inference, graph output, and evaluation. Future API, database, frontend, identity provider, external integrations, and deployment infrastructure are outside the core boundary. Imported events and future user-provided files are untrusted input. Ground truth is an evaluation-only boundary and must not enter prediction logic.

## 5. Component responsibilities

- **Synthetic scenario generator:** Creates controlled attack scenarios, clean ground truth, and configurable observation imperfections.
- **Event ingestion and validation:** Accepts structured records, enforces schema and size limits, rejects malformed input, and reports errors without executing content.
- **Normalization:** Converts accepted records into a stable internal representation while recording transformations.
- **Original evidence preservation:** Stores immutable or content-addressed source records separately from normalized records.
- **Candidate relationship generation:** Finds plausible pairs or groups using observable features and explicit windows; it must not use expected labels.
- **Evidence scoring:** Scores supporting and contradicting signals with a documented, deterministic policy.
- **Attack-graph reconstruction:** Selects or ranks proposed relationships and produces an explainable graph.
- **Uncertainty and alternative hypotheses:** Preserves confidence, ambiguity, rejected candidates, and competing explanations.
- **Incremental reconstruction:** Incorporates newly arrived or delayed observations without silently changing historical evidence.
- **Independent evaluator:** Compares prediction output with separately supplied ground truth only after reconstruction.
- **Experiment runner and metrics:** Records configuration, seed, data version, output, and reproducible metrics.
- **Command-line interface:** Provides local, service-independent execution and inspection commands.
- **Future FastAPI backend:** Provides authenticated, authorized HTTP access to core operations; it must not contain the core algorithm.
- **Future PostgreSQL persistence:** Stores experiments, evidence metadata, graphs, and audit records with migrations and least privilege.
- **Future React dashboard:** Provides the five approved investigation screens and safe rendering of untrusted event values.
- **Docker when justified:** Packages verified services for repeatable integration or deployment; it is not required for the foundation.

## 6. Data flow

```text
Scenario definition and independent ground truth
  -> Observed synthetic evidence generation
  -> Ingestion and validation
  -> Normalization
  -> Candidate relationship generation
  -> Evidence evaluation
  -> Graph reconstruction
  -> Reconstruction output
  -> Independent evaluation against ground truth
  -> Metrics and experiment reports
  -> Optional persistence and visualization
```

The reconstruction algorithm must not receive expected relationship labels during prediction. Ground truth is held outside that path and introduced only to the independent evaluator.

## 7. Proposed normalized event schema

The proposed event fields are:

- `event_id`: stable identifier for the source event or its preserved identity.
- `scenario_id`: synthetic scenario identifier, kept separate from event identity.
- `event_type`: controlled event category.
- `event_time`: time at which the activity is believed to have occurred.
- `observed_time`: time at which the record was collected or arrived.
- `host_id`: observed host identity, if known.
- `user_id`: observed user identity, if known.
- `source_ip`: observed network source, if known.
- `process_id`: observed process identifier, if known.
- `session_id`: observed session identifier, if known.
- `source`: originating sensor or log source.
- `attributes`: explicitly unstructured, untrusted event details retained for analysis.

`event_time` differs from `observed_time`; delayed delivery must not be mistaken for activity order. Unknown identity values must not match merely because both are missing. The exact types, timezone policy, validation library, and canonical serialization remain decisions for Master Prompt 2.

## 8. Reconstruction and uncertainty

Candidate generation should use observable evidence such as compatible time windows, known identifiers, host and process context, and source-specific signals. Evidence scoring must expose the signals used, missing signals, contradictions, and any thresholds. A graph edge means a proposed relationship supported by available evidence, not proven causation. The system must distinguish chronological order, correlation, inference, and causation. Alternative hypotheses should remain inspectable rather than being discarded solely because one candidate ranked higher.

## 9. Ground-truth isolation

Scenario truth is created independently from the observed evidence. The predictor receives observed records and configuration only. The evaluator receives reconstruction output and ground truth after prediction. Tests should detect accidental leakage by changing labels without changing observations and by checking that prediction output does not contain hidden truth fields.

## 10. Evaluation methodology

Evaluation will define event-level and relationship-level matching rules before experiments. Candidate metrics may include precision, recall, F1, false-positive rate, false-negative rate, ordering quality, calibration or confidence quality, and robustness by impairment type. Every report must include dataset/scenario version, seed, configuration, metric definitions, and limitations. No metric is implemented or claimed yet.

## 11. Security architecture and trust boundaries

Imported JSON/CSV content crosses into the core as untrusted data. Future API requests cross an HTTP trust boundary and require authentication, authorization, request limits, and safe error handling. Future PostgreSQL is a separate data trust boundary requiring parameterized access and least privilege. A future browser is an untrusted presentation boundary; event text must be escaped and external links constrained. Ground truth is a research trust boundary protected from prediction code. Malicious imports, forged identities, timestamp manipulation, duplicate manipulation, oversized input, misleading correlations, and ground-truth leakage are explicit threats.

## 12. Authentication and authorization principles

The standalone core has no accounts and therefore no authentication implementation. A future API must separate authentication from authorization, default to deny, enforce resource and organization context on the backend, protect administrative operations, and audit security decisions. Tenant-specific controls are conditional until multi-tenant functionality exists. Secrets must come from managed configuration, never source files or event data.

## 13. Audit and monitoring design

Future application audit records will be distinct from imported forensic records and reconstructed hypotheses. Records should include actor, action, target, time, outcome, request context, and a redacted reason where appropriate. Audit integrity, restricted access, retention, suspicious activity monitoring, authorization failures, privilege changes, and failure behavior must be designed before the API is introduced. Never log passwords, reusable tokens, raw recovery codes, or secret credentials.

The planned taxonomy is: `LOGIN`, `LOGOUT`, `LOGIN_FAILURE`, `SIGNUP`, `EMAIL_VERIFICATION`, `PASSWORD_CHANGE`, `PASSWORD_RESET`, `MFA_ENABLED`, `MFA_DISABLED`, `MFA_FAILURE`, `SESSION_CREATED`, `SESSION_REVOKED`, `ROLE_CHANGED`, `PERMISSION_CHANGED`, `ORG_CREATED`, `ORG_MEMBER_ADDED`, `ORG_MEMBER_REMOVED`, `API_KEY_CREATED`, `API_KEY_REVOKED`, `INTEGRATION_CONNECTED`, `INTEGRATION_DISCONNECTED`, `SCAN_STARTED`, `SCAN_COMPLETED`, `SCAN_FAILED`, `SCOPE_CHANGED`, `SECURITY_DECISION_CREATED`, and `SECURITY_DECISION_CHANGED`. Only scan lifecycle and security-decision events are potentially applicable to the current research core; identity, organization, API-key, integration, and MFA events depend on future functionality.

## 14. Implemented modules and technology choices

Python standard-library modules, FastAPI, Pydantic, SQLAlchemy, psycopg, React, TypeScript, Vite, React Router, Lucide, and pytest are used. `models.py` validates and normalizes events, `scenarios/generator.py` creates deterministic observations and separate truth, `ingestion.py` loads safe JSON and reports invalid/duplicate records, `reconstruction.py` generates bounded candidates and scores evidence, `graph.py` serializes graph hypotheses, `evaluation.py` computes metrics after prediction, `api.py` exposes typed routes, `persistence.py` defines PostgreSQL models, and `frontend/src` implements the five connected screens. The API explicitly falls back to memory only when `DATABASE_URL` is absent; this fallback is not persistent storage. Docker and release tooling remain Master Prompt 4 work.

## 15. Repository structure

```text
ECHO/
  README.md
  pyproject.toml
  .gitignore
  docs/
    Architecture.md
    SecurityChecklist.md
    memory.md
  src/
    echo/
      __init__.py
      __main__.py
      cli.py
      models.py
      ingestion.py
      reconstruction.py
      graph.py
      evaluator.py
      evaluation.py
      api.py
      persistence.py
      scenarios/
        generator.py
  tests/
    unit/
      test_cli.py
      test_engine.py
      test_api.py
  frontend/
    src/
    package.json
  migrations/
    001_initial.sql
```

Directories are created when they contain implementation; unnecessary empty directories are avoided.

## 16. Testing strategy

Use focused unit tests for parsing, normalization, candidate generation, scoring, graph behavior, and metrics. Add property or fuzz-style malformed-input tests where useful, integration tests for the full core flow, leakage tests for ground-truth isolation, deterministic repeatability tests, and security tests for resource limits and safe errors. Future API, database, authorization, tenant-isolation, frontend, migration, and deployment tests should be added with those components.

## 17. Error handling

Reject malformed or oversized inputs with stable, non-sensitive error categories. Preserve enough internal diagnostic context for debugging while redacting secrets and avoiding stack traces in external responses. A failed transformation must not silently destroy original evidence. Partial or rejected records should be represented explicitly in experiment results.

## 18. Deployment considerations

The core must remain independently executable and testable without an API, database, or frontend. Local development uses a Windows virtual environment. Future deployments need environment separation, secret management, TLS, least-privilege service accounts, dependency and container scanning, restricted network exposure, backups when persistence exists, and documented recovery behavior.

## 19. Risks and limitations

The proposed schema and architecture are not fully implemented. Synthetic scenarios may not represent real environments. Correlation is not causation. Missing or forged fields can make hypotheses ambiguous. Thresholds may encode bias. Ground-truth quality controls evaluation quality. Resource limits and scalability are unresolved. The foundation has no authentication, persistence, API, frontend, or production hardening.

## 20. Evaluation methodology

The evaluator matches exact `(source_event_id, target_event_id, relationship_type)` tuples after reconstruction. It reports edge precision, edge recall, edge F1, false-link rate (`FP / predicted edges`), reconstruction coverage (`ground-truth relationship endpoint events represented by predicted edges / eligible endpoint events`), ordering accuracy, and runtime. Zero-denominator values are reported as `0.0` under an explicit policy and are not interpreted as perfect performance. Ordering accuracy is currently `0.0` because the current truth schema has relationship targets but no separate ordering labels.

## 21. Unresolved decisions

Future work must decide broader event-type coverage, richer candidate-window strategies, calibrated uncertainty if justified, graph version persistence, baseline metrics, identity/authentication design, persistence schema, API contracts, UI data exposure, deployment topology, retention, and release acceptance criteria.

## Current verification status

Verified in Master Prompt 4: all Master Prompt 3 capabilities, explicit local CORS, accessible investigation creation, dashboard synthetic import, idempotent repeated event imports, graph-node and timeline selection, live fallback workflow, desktop/mobile browser rendering, and zero browser console errors. Not verified: live PostgreSQL connectivity, migration execution against PostgreSQL, API repository wiring to SQLAlchemy persistence, authentication, authorization, production hardening, or scientific benchmark validity.
