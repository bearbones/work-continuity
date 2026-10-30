# Integration and data contracts

These are proposed application contracts, not existing SDK APIs. Field names and examples define implementation intent. The synthetic fixture is a compact scenario format rather than a complete database export.

## Identity and source revisions

Use a namespaced `source_key = deployment / connector / container / native_id`. Store each revision under a separate `revision_id`; never deduplicate different authors or systems solely by matching text. Deduplication of delivery is separate from recognizing copied evidence.

| SourceRevision field | Meaning |
| --- | --- |
| `revision_id`, `source_key`, `upstream_revision` | Stable local revision, logical source identity, and optional upstream version |
| `kind`, `actor_id`, `actor_role` | Message, note, issue, PR, tool result, etc.; human or agent/tool attribution |
| `parent_key`, `thread_key`, `links` | Native context and explicit cross-record links |
| `occurred_at`, `source_updated_at`, `observed_at` | Event, upstream revision, and ingestion clocks |
| `time_precision`, `source_timezone` | Preserve date-only or interval meaning |
| `payload_ref`, `normalized_text`, `content_hash` | Retained payload, searchable representation, integrity check |
| `scope_id`, `access_policy_ref`, `access_checked_at` | Authorization and freshness |
| `origin_family_id`, `derived_from` | Copied/derived evidence lineage |
| `supersedes_revision_id`, `tombstone_reason` | Edit or removal semantics |
| `connector_version`, `normalizer_version` | Reproducibility metadata |

Evidence spans reference a specific revision and a stable location: message field, JSON pointer, diff hunk with base/head identifiers, tool-output segment, or text offsets plus a text hash. A URL alone is insufficient when a page can change. Store normalized text consistently before computing offsets.

A source edit supersedes the previous revision for current reading but may leave it available for permitted historical queries. A deletion or access revocation can make all revisions unavailable regardless of historical interest.

## Canonical records

### ClaimRevision

```text
claim_id, claim_revision_id
subject_id, predicate, object_id_or_value
scope_id, qualifiers
asserted_by, assertion_mode          # reported | inferred | explicit_user_direction
evidence[]                          # span ID plus supports/contradicts/qualifies
origin_family_ids[]
assessment                          # proposed | supported | disputed | retracted | superseded
authority_rule_id                    # nullable; authority is field/scope-specific
valid_from, valid_to, validity_precision, validity_unknown
recorded_from, recorded_to
processing_run_id, overrides_claim_revision_id
```

`assessment=supported` means supported under the recorded assessment criteria, not universal truth. A claim “the assistant reported success” and a claim “the test passed” have different predicates and evidence requirements.

Claim revisions are append-only within applicable retention. Closing a recording interval can be represented by a separate revision event. The current projection is derived from those events. Keep enough data to reconstruct prior state without rerunning the model.

### WorkReference

```text
work_id, external_refs[], title, intended_outcome
authority_home, authority_policy_version, field_authorities{}
upstream_status, normalized_status, status_revision_id
owner_refs[], owner_ambiguity
due_at, review_after, completion_criteria[]
parent_id, dependency_ids[], evidence_ids[]
last_successful_refresh, source_coverage
```

Normalize statuses into a small display vocabulary such as proposed, active, waiting, completed, cancelled, and unknown, while retaining original status and the connector-specific mapping. A tracker transition to “resolved” need not map to completed if that workflow distinguishes verification. Store the mapping as configuration, not a model guess.

### Episode and summary

An Episode contains a stable ID, revision ID, objective, member source revisions, participants, time range, attempted approaches, decisions, observed outcomes, open questions, and focal work references. Its structured elements reference evidence.

A Summary contains scope, kind, body, direct input IDs, transitive source dependencies, generation ID, model/prompt versions, time window, knowledge cutoff, and stale/quarantined status. Transitive dependencies may be materialized or computable through a derivation table. Invalidating a leaf must reliably find affected summaries and cards.

### UserDirection and Correction

UserDirection records author, goal or preference, scope, effective interval, priority, and superseded version. It cannot originate from untrusted retrieved prose.

Correction records target IDs, operation, reason, user-authenticated author, scope, effective time, and recorded time. Operations include reject interpretation, replace inferred value, split/merge identity, mark evidence insufficient, and change explicit direction. Corrections to upstream state are proposals until a write receipt verifies them.

Identity merges preserve an alias history and can be reversed. Reversal invalidates derived relationships and summaries that crossed the mistaken identity boundary.

## Connector interface

```text
capabilities() -> ConnectorCapabilities
scan(cursor, scope) -> ChangePage
fetch(source_key, revision_hint?) -> SourceRevision | NotFound | AccessDenied
resolve_link(url_or_native_id) -> SourceKey | Ambiguous | Unsupported
check_access(principal, source_keys) -> AccessDecisions
prepare_change(intent, expected_revision) -> PreparedChange       # optional
apply_change(prepared_change, idempotency_key) -> WriteReceipt     # optional
```

Capabilities declare whether the source exposes webhooks, incremental cursors, revision history, edits, tombstones, ACL changes, conditional writes, and native idempotency. The service does not assume these exist. A polling connector without deletion events needs periodic scoped reconciliation. A connector without historical versions can preserve only revisions it actually observes; report that coverage limitation.

Changes include upsert, delete, access_changed, and checkpoint. A `ChangePage` carries events, next cursor, source time, and an indication of whether the scan is complete. Persist events and queue work transactionally before advancing the cursor. Deduplicate webhook and polling deliveries using source identity and upstream revision or content hash.

Backfill uses the same normalization path as live ingestion. Retry with exponential backoff and jitter, honor source rate limits, and distinguish transient errors from malformed data and lost authorization. Quarantine malformed records with an inspectable reason. Never retry a non-idempotent external write merely because the network timed out.

## Adapter mapping examples

| Source | Deterministic data | Interpretation opportunities | Special care |
| --- | --- | --- | --- |
| Hierarchical work tracker | IDs, owners, state, parent links | Missing rationale and implicit dependencies | Preserve actual hierarchy and status semantics |
| Lightweight shared issue project | Commitment records and explicit links | Relate follow-ups to larger objectives | Avoid duplicating authoritative tickets |
| 1:1 notes | Participants, meeting date, note revisions | Candidate promises and follow-ups | Private scope and uncertain action assignment |
| Conversations | Thread, author, message edits, links | Decisions and work context | Quoted claims, proposals, humor, missing threads |
| PR/code host | Revision, reviews, checks, merge state | Rationale and affected objectives | Merge is not rollout; checks are revision-specific |
| Agent sessions | Roles, turns, tool calls/results | Resumption context and attempted approaches | Generated assertions versus observed tool evidence |

Each adapter maps source roles into the canonical contracts. No specific internal service endpoints, auth method, or client extension mechanism is assumed.

## Retrieval backend interface

```text
project(changes, generation, policy_version) -> ProjectionReceipt
search(query_plan) -> CandidateSet
neighbors(entity_ids, relation_types, budget) -> CandidateSet
invalidate(dependency_ids, reason) -> InvalidationReceipt
erase(source_revision_ids) -> ErasureReceipt
health() -> watermarks, failures, generation, backend_version
```

`QueryPlan` includes principal-derived scope, purpose, focal IDs, world time, knowledge cutoff, filters, token/result/traversal budgets, and projection generation. Clients cannot supply an arbitrary partition to bypass authorization. Derive allowed partitions on the server.

`CandidateSet` includes canonical IDs, backend IDs, score provenance, matched passages or mapping references, time qualifiers, source generation, truncation metadata, and warnings. A score is a ranking signal, not truth confidence. Unmapped backend objects cannot support a factual answer.

## Client service API

The internal client can call an authenticated HTTP or equivalent in-process API. These route names are illustrative; retain semantics when adapting them to the host application.

| Operation | Input | Response |
| --- | --- | --- |
| `GET /v1/attention` | Context, limit, cursor | Ranked cards, suppression summary, freshness |
| `GET /v1/work/{id}/resume` | Optional historical mode | Resumption packet, evidence, open questions |
| `POST /v1/query` | Question, scope, purpose, time mode | Answer, claim-level evidence, coverage, warnings |
| `GET /v1/evidence/{id}` | Evidence ID | Authorized revision excerpt and source link |
| `POST /v1/feedback` | Card ID, feedback type, revision | Receipt; no implicit tracker transition |
| `POST /v1/corrections` | Target, correction, expected version | Correction receipt and invalidated objects |
| `POST /v1/actions/prepare` | Intent and target | Concrete proposed change with preconditions |
| `POST /v1/actions/{id}/execute` | Authorization and expected version | Applied, rejected, or outcome-unknown receipt |

The last two operations are disabled in the first pilot. Requests derive principal identity from authentication, never from a user-controlled `principal_id` body field. Evidence endpoints recheck current access, including on historical answers. Cached cards and answers are keyed by authorized scope, policy version, time mode, and dependency generation.

An attention card has `card_id`, `revision`, `work_id`, `title`, `reason_code`, `why_now`, `known_state`, `suggested_next_step`, `evidence_ids`, `uncertainties`, `source_freshness`, `suppression_key`, and `allowed_actions`. Reason codes make ranking explainable: new_blocker, unblocked, review_requested, follow_up_due, possible_completion, or resume_context.

Distinguish `not_found`, `not_authorized`, `source_unavailable`, `projection_stale`, and `insufficient_evidence` internally. Public responses must not reveal forbidden object existence through detailed errors. A stale backend can yield an authorized narrower answer with a clear freshness marker.

## Optional external writeback

External writes require explicit user intent or an established scoped automation rule. Memory relevance does not confer authority to send messages or assign work.

An ActionIntent records target source and object, exact patch, rationale/evidence, expected source revision, authorization identity/rule, expiry, and idempotency key. Preparation shows the actual change. Execution rereads the target and rejects stale preconditions rather than overwriting newer work.

Lifecycle: prepared → authorized → executing → applied, rejected, or outcome_unknown. After a timeout, reconcile with the source before any retry. An applied receipt includes upstream revision/ID and a readback verification. The next connector scan associates that mutation with the intent to avoid self-generated notification loops.

If the connector cannot support reliable conditional writes, restrict the capability to a draft or deep link until a safe reconciliation strategy is implemented. User confirmation is not a substitute for concurrency control.

## Data handling and reliability

Place application data outside the public checkout. Use the target environment's identity, storage protection, model endpoints, and retention controls. Limit archive acquisition to configured scopes; a “local archive” need not mean copying every accessible conversation. Do not collect credentials or unnecessary hidden metadata from session files.

Deletion has two phases: immediate exclusion from all read paths, then verified cleanup of content-bearing artifacts. Track source revisions, canonical claims, backend episode IDs, embeddings, summaries, caches, and pending cards. If any component cannot confirm removal, retain the quarantine. Backup retention and restore must honor tombstones so a restore does not resurrect erased content.

Keep a transactional outbox for projection and optional write jobs. Processing is at-least-once with idempotency, not an unsupported claim of exactly-once execution. Replay the same event twice without duplicating commitments or alerts. Serialize conflicting updates to the same canonical object and graph partition.
