# ECHO Security Checklist

**Status vocabulary:** Not started, In progress, Blocked, Verified complete, Not applicable. A control is `Verified complete` only when supporting evidence exists. `Evidence reference` points to a test, configuration, design decision, or review artifact; `None yet` is valid.

**Current scope:** Master Prompt 1 is a standalone synthetic-data Python foundation with no accounts, network API, database, frontend, external integration, or production deployment. Future-only controls remain conditional and incomplete.

## 1. Authentication and account security

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| AUTH-001 | Protect login from automated abuse | High | Future accounts/API | Security test and rate-limit review | Not applicable | None yet; no login |
| AUTH-002 | Prevent brute-force and credential-stuffing attacks | High | Future accounts/API | Negative tests and monitoring review | Not applicable | None yet; no login |
| AUTH-003 | Apply per-user and per-origin rate limits | High | Future network API | Integration test and configuration review | Not applicable | None yet; no API |
| AUTH-004 | Use lockout or progressive delays without account enumeration | High | Future accounts | Abuse-case tests | Not applicable | None yet |
| AUTH-005 | Add CAPTCHA or equivalent bot protection where risk warrants | Medium | Future public signup/login | Threat-model decision and test | Not applicable | None yet |
| AUTH-006 | Hash passwords with a current adaptive password KDF | Critical | Future accounts | Configuration and password-hash test | Not applicable | None yet |
| AUTH-007 | Enforce a documented password policy | High | Future accounts | Policy test | Not applicable | None yet |
| AUTH-008 | Secure signup, duplicate-account handling, and email verification | High | Future accounts | Integration tests and enumeration review | Not applicable | None yet |
| AUTH-009 | Expire and invalidate email-verification tokens | High | Future accounts | Token lifecycle test | Not applicable | None yet |
| AUTH-010 | Secure password reset, expire single-use tokens, and invalidate sessions afterward | Critical | Future accounts | End-to-end reset test | Not applicable | None yet |
| AUTH-011 | Never disclose credentials or reusable authentication material | Critical | Any authentication path | Log/response secret scan | Not applicable | No authentication exists |

## 2. Session security

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| SESS-001 | Generate unpredictable session and token identifiers | Critical | Future API/accounts | Entropy and code review | Not applicable | None yet |
| SESS-002 | Set HttpOnly, Secure, and appropriate SameSite cookie flags | High | Cookie sessions | Browser and header tests | Not applicable | None yet |
| SESS-003 | Enforce idle and absolute session expiration | High | Future accounts | Session lifecycle tests | Not applicable | None yet |
| SESS-004 | Rotate sessions after login and sensitive changes to prevent fixation | Critical | Future accounts | Integration test | Not applicable | None yet |
| SESS-005 | Invalidate sessions on logout and security events | High | Future accounts | Integration test | Not applicable | None yet |
| SESS-006 | Define concurrent-session handling and safe session-identifier storage | Medium | Future accounts | Design review and test | Not applicable | None yet |
| SESS-007 | Protect refresh tokens with rotation, revocation, and secure storage | Critical | Future token API | Token lifecycle tests | Not applicable | None yet |

## 3. Multi-factor authentication

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| MFA-001 | Secure MFA enrollment and change confirmation | High | Future accounts | Integration tests | Not applicable | None yet |
| MFA-002 | Protect TOTP secrets and verify codes safely | High | Future MFA | Secret-storage and replay tests | Not applicable | None yet |
| MFA-003 | Generate, display, and consume recovery codes safely | High | Future MFA | Lifecycle and logging tests | Not applicable | None yet |
| MFA-004 | Protect MFA reset and recovery from takeover | Critical | Future MFA | Abuse-case tests | Not applicable | None yet |
| MFA-005 | Enforce MFA for configured roles and prevent bypass | High | Future MFA | Authorization tests | Not applicable | None yet |
| MFA-006 | Define session behavior after MFA changes and audit MFA events | High | Future MFA | Session and audit tests | Not applicable | None yet |
| MFA-007 | Evaluate WebAuthn/passkeys as a future enhancement | Low | Future accounts | Architecture decision record | Not applicable | None yet |

## 4. Authorization, access control, and RBAC

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| AUTHZ-001 | Separate authentication from authorization with default deny | Critical | Future API | Authorization unit tests | Not applicable | Core has no accounts |
| AUTHZ-002 | Enforce RBAC and protect role modification | High | Future accounts/admin | Role matrix and tests | Not applicable | None yet |
| AUTHZ-003 | Check resource/object ownership and prevent IDOR/BOLA | Critical | Any persisted/API resource | Horizontal authorization tests | Not applicable | No resources/API |
| AUTHZ-004 | Protect administrative endpoints and test vertical escalation | Critical | Future admin/API | Negative integration tests | Not applicable | None yet |
| AUTHZ-005 | Enforce organization/tenant isolation in backend authorization and data access | Critical | Conditional: future SaaS | Tenant-isolation tests | Not applicable | SaaS not introduced |
| AUTHZ-006 | Secure membership, invitations, permission inheritance, and resource ownership | High | Conditional: future SaaS | Workflow and access tests | Not applicable | None yet |
| AUTHZ-007 | Authorize every customer-data request in the correct tenant context, not only in UI | Critical | Conditional: future SaaS | API/data-layer tests | Not applicable | SaaS not introduced |

## 5. Error message security

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| ERR-001 | Do not disclose passwords, tokens, API keys, or credentials | Critical | All components | Response and log secret scan | In progress | No secrets introduced in foundation files |
| ERR-002 | Do not return production stack traces, raw database errors, paths, or infrastructure details | High | Future API/UI | Error-response tests | Not applicable | No API |
| ERR-003 | Use consistent external errors and protected internal diagnostics | High | Future API | Contract and logging tests | Not applicable | None yet |
| ERR-004 | Redact secrets and sensitive event data in diagnostics | Critical | Core and future services | Redaction unit tests | Not started | None yet |

## 6. Backend and API security

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| API-001 | Validate input schemas and output encoding | Critical | Core/API | Malformed-input and serialization tests | Not started | Core ingestion is future |
| API-002 | Enforce request/file size and resource limits | High | Import/API | Boundary and exhaustion tests | Not started | None yet |
| API-003 | Apply authentication, authorization, rate limits, versioning, and restrictive CORS | Critical | Future API | Integration and header tests | In progress | Local API has restrictive localhost CORS and validation; auth/rate limits remain future |
| API-004 | Apply CSRF protection where cookie authentication is used | High | Future browser API | Browser/integration tests | Not applicable | No API |
| API-005 | Prevent SSRF, SQL/NoSQL injection, command injection, and path traversal | Critical | Future integrations/API/storage | Security tests and code review | Not applicable | No such paths |
| API-006 | Prevent unsafe deserialization and unsafe file-upload processing | Critical | Import/API | Payload tests and review | Not started | Importer is future |
| API-007 | Verify webhooks, prevent replay, and use idempotency where applicable | High | Future integrations | Signature/replay tests | Not applicable | No webhooks |
| API-008 | Protect API keys and OAuth flows with least privilege and secure storage | Critical | Future integrations | Secret scan and protocol tests | Not applicable | No integrations |
| API-009 | Prevent GraphQL abuse, pagination abuse, mass assignment, and resource exhaustion if those features are chosen | High | Conditional future API | Design decision and abuse tests | Not applicable | GraphQL not selected |
| API-010 | Set security headers and scan dependencies | High | Future API/frontend/build | Header check and dependency scanner | In progress | Backend/frontend dependencies installed; header scan remains |

## 7. Logging and monitoring

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| LOG-001 | Define and emit appropriate application audit events | High | Future application/API | Taxonomy review and tests | In progress | Taxonomy in Architecture.md |
| LOG-002 | Distinguish application audit events, imported forensic records, and reconstructed hypotheses | Critical | Core and future services | Data-model and provenance tests | In progress | Architecture.md boundary design |
| LOG-003 | Protect audit integrity, access, retention, and failure behavior | High | Future persistence | Threat model and integration tests | Not applicable | No audit store |
| LOG-004 | Monitor suspicious activity, authorization failures, and privilege changes | High | Future application | Detection tests and alert review | Not applicable | No account system |
| LOG-005 | Never log passwords, reusable tokens, raw recovery codes, or secret credentials | Critical | All components | Automated log scan and review | In progress | Foundation has no secret logging |

### Audit-event taxonomy

The planned taxonomy is: `LOGIN`, `LOGOUT`, `LOGIN_FAILURE`, `SIGNUP`, `EMAIL_VERIFICATION`, `PASSWORD_CHANGE`, `PASSWORD_RESET`, `MFA_ENABLED`, `MFA_DISABLED`, `MFA_FAILURE`, `SESSION_CREATED`, `SESSION_REVOKED`, `ROLE_CHANGED`, `PERMISSION_CHANGED`, `ORG_CREATED`, `ORG_MEMBER_ADDED`, `ORG_MEMBER_REMOVED`, `API_KEY_CREATED`, `API_KEY_REVOKED`, `INTEGRATION_CONNECTED`, `INTEGRATION_DISCONNECTED`, `SCAN_STARTED`, `SCAN_COMPLETED`, `SCAN_FAILED`, `SCOPE_CHANGED`, `SECURITY_DECISION_CREATED`, and `SECURITY_DECISION_CHANGED`.

`SCAN_STARTED`, `SCAN_COMPLETED`, and `SCAN_FAILED` can apply to future ECHO experiments. `SCOPE_CHANGED` and security-decision events can apply to future investigation workflows. Login, signup, email, password, MFA, session, role, permission, organization, API-key, and integration events depend on future accounts, SaaS, or integrations. They are not emitted by the current standalone CLI.

## 8. Data protection and forensic integrity

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| DATA-001 | Preserve original imported evidence separately from normalized records | Critical | Future ingestion | Provenance and immutability tests | In progress | `models.py` preserves `original_payload`; persistence is future |
| DATA-002 | Record transformations, validate identifiers/timestamps, and represent missing values explicitly | High | Future ingestion | Schema and transformation tests | In progress | `models.py` and `test_engine.py` |
| DATA-003 | Handle duplicates without silently destroying evidence | High | Future ingestion | Duplicate fixtures and report review | In progress | `ingestion.py` and duplicate test |
| DATA-004 | Protect JSON/CSV imports, reject malformed/oversized content, and never execute imported content | Critical | Future ingestion | Malicious fixture and limit tests | In progress | JSON validation and file-size limit in `ingestion.py`; broader fixtures remain |
| DATA-005 | Keep ground truth separate from prediction logic | Critical | Research engine | Leakage tests and code review | Verified complete | Separate generator/evaluator interfaces and isolation test |
| DATA-006 | Preserve experiment configuration, seeds, inferred-relationship provenance, retention, and deletion behavior | High | Research engine/persistence | Reproducibility and lifecycle tests | Not started | None yet |

## 9. Frontend security

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| UI-001 | Escape untrusted event data and prevent XSS | Critical | Future React UI | Browser security tests | In progress | React renders API values as text; browser security tests remain |
| UI-002 | Handle tokens securely and make UI behavior authorization-aware | Critical | Future React/API | Architecture and browser tests | Not applicable | No frontend |
| UI-003 | Protect external links, CSRF flows, dependency supply chain, error states, and admin routes | High | Future React/API | Browser and dependency tests | Not applicable | No frontend |

## 10. Database and infrastructure security

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| INFRA-001 | Use least-privilege database access and parameterized queries | Critical | Future PostgreSQL | Migration/code review and injection tests | In progress | SQLAlchemy models and migration SQL; live DB test unavailable |
| INFRA-002 | Manage secrets outside source and encrypt traffic and stored data where appropriate | Critical | Future deployment | Configuration and TLS review | In progress | `.env.example` contains placeholders only; TLS/deployment remain |
| INFRA-003 | Use safe migrations, backups/recovery, environment separation, and restricted network exposure | High | Future persistence/deployment | Migration, restore, and infrastructure tests | Not applicable | None yet |
| INFRA-004 | Scan dependencies and containers; restrict administrative access | High | Future services | CI evidence and access review | Not started | No CI/services |

## 11. External integrations

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| EXT-001 | Use least-privilege OAuth scopes and securely store/rotate credentials | Critical | Future integrations | Protocol and secret-storage tests | Not applicable | No integrations |
| EXT-002 | Verify webhook signatures, prevent replay, revoke access, and enforce idempotency | High | Future webhooks | Replay/signature tests | Not applicable | No webhooks |
| EXT-003 | Document external trust boundaries and apply SSRF protections | High | Future outbound calls | Threat model and network tests | Not applicable | No outbound calls |

## 12. Secure development and release

| ID | Requirement | Priority | Applies when | Verification method | Status | Evidence reference |
|---|---|---|---|---|---|---|
| SDLC-001 | Maintain security unit, integration, authorization, malformed-input, and regression tests | High | All implemented features | Test reports and review | In progress | `tests/unit/test_engine.py` and `tests/unit/test_cli.py`; API tests remain future |
| SDLC-002 | Add tenant-isolation tests when multi-tenant functionality exists | Critical | Conditional future SaaS | Automated authorization suite | Not applicable | SaaS not introduced |
| SDLC-003 | Run dependency checks, configuration review, and threat modeling | High | Release candidates | CI artifacts and review records | In progress | This checklist and Architecture.md |
| SDLC-004 | Require evidence-backed release acceptance, documented limitations, and residual risks | High | Every release | Release checklist | In progress | Master Prompt 1 completion record |

## 13. Threat model

### Assets

Original imported evidence, normalized records, provenance, inferred relationships, hypotheses, ground truth, experiment configurations and seeds, metrics, future credentials, audit records, and user/tenant data are assets. Integrity and confidentiality of ground truth and imported evidence are especially important for research validity.

### Trust boundaries and entry points

Entry points are local CLI arguments and future JSON/CSV imports. Future HTTP clients, browsers, databases, identity providers, webhooks, and external services add boundaries. Imported content crosses from an untrusted file into the processing core; future API input crosses from an untrusted network client into service code; future UI output crosses into a browser.

### Abuse cases and mitigations

- Malicious imported records: validate schemas, limit size, preserve raw data, treat values as data, and never execute content.
- Forged identities: label observed identities as claims, preserve source/provenance, and avoid treating a field as verified identity.
- Timestamp manipulation: validate formats and ranges, preserve both event and observed time, and surface conflicts.
- Duplicate manipulation: retain duplicate evidence, assign deterministic duplicate metadata, and avoid silent deletion.
- Oversized input: enforce file, record, graph, and processing budgets with safe failure behavior.
- Misleading correlations: expose evidence and contradictions, distinguish inference from causation, and retain alternatives.
- Ground-truth leakage: isolate truth from prediction code and run leakage tests.
- Future account takeover or privilege escalation: use secure sessions, MFA options, default-deny authorization, and audit events before enabling accounts.

### Residual risks

Synthetic data may underrepresent adversarial real-world telemetry. Inference can be wrong even with good evidence. Future thresholds, schemas, persistence, and integrations can introduce new risks. These risks remain open and prevent production-readiness claims.

## 14. Future capabilities and conditions

SaaS accounts, tenant management, MFA enforcement, production deployment, external integrations, OAuth, webhooks, and passkeys are conditional future capabilities. Their controls must remain incomplete until the capability is introduced, implemented, tested, and evidenced. No future control is marked complete by this document.

## Current evidence

The current foundation contains no authentication, sessions, API, database, frontend, external integrations, file importer, or deployment service. The only executable security-relevant evidence is the small CLI test and the absence of credentials in the created files. This is not a security assessment or production approval.
