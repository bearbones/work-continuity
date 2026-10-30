# Implementation plan

## Starting position

This repository is an implementation handoff, not a running prototype. Begin in the workplace environment with access to the intended client and approved sources. Keep this generic design public and create the implementation and data stores in locations suitable for their contents. No internal integration has been inspected or assumed here.

The first slice is one person, one project, one tracker, and one notes/session source. Deliver a read-only Resume view and a small on-demand attention digest. Reflection and proactive notifications come later.

## Workplace discovery

Resolve these questions by inspecting the actual systems before selecting libraries or building connectors:

| Question | Decision it informs |
| --- | --- |
| How does the existing client support extensions or service calls? | API/authentication and rendering boundary |
| Which record owns objective status, task status, owner, and follow-up state? | Per-field authority configuration |
| Which source exposes revisions, edits, deletions, ACL changes, and stable links? | Connector coverage and reconciliation strategy |
| Can a small project be exported for a bounded pilot? | Offline replay before live ingestion |
| Which local or server storage and model endpoints are available? | Deployment and extraction/reader choices |
| Are notes private to one person or shared? | Partitioning and whether mixed-source summaries are permitted |
| What is currently forgotten or expensive to resume? | First useful case and pilot rubric |
| What would count as a useful interruption? | Attention eligibility and suppression rules |

Record decisions in a short deployment configuration and an implementation decision log. Do not put actual private source IDs, endpoint URLs, or records into the public design repository.

## Milestone 0 — Contracts and offline examples

Deliver a schema-validated canonical model, connector capability interface, authority configuration, and scenario replay harness. Begin with the supplied synthetic scenario and add the adversarial cases from the evaluation plan.

Choose a single supported runtime and pin dependencies. Python is a reasonable initial proposal because both optional research backends expose Python integrations; the client can remain in its host application's language. Runtime choice should follow the actual environment.

Exit when a source revision, inferred claim, explicit commitment, correction, and historical knowledge query can be represented without ambiguity. Prove that a merged PR cannot automatically complete the synthetic investigation. No LLM or external service is needed to validate these semantics.

## Milestone 1 — Archive and canonical ledger

Implement one read-only connector and a manual JSON import adapter. Preserve source identity, revision, actor role, event time, observation time, and permitted content. Add a durable queue/outbox, ingestion receipts, cursor handling, and a coverage status endpoint.

Implement corrections, tombstones, dependency invalidation, and a basic restore/replay path before large-scale ingestion. Keep application data outside the source checkout.

Exit when duplicate deliveries are harmless, edits preserve appropriate history, a crash cannot advance past an unrecorded event, and erasure excludes content immediately. Demonstrate replay of the synthetic delayed handoff and retracted completion inference.

## Milestone 2 — Useful baseline without a graph framework

Add lexical retrieval, a compatible embedding index, explicit link traversal, and source-backed episode accounts. Use deterministic tracker fields directly. Add a small source-grounded extraction prompt only where unstructured material requires interpretation.

Implement a context packet with authority, evidence, time qualifiers, and missing-data indicators. Use a stronger reader during initial diagnosis, then compare smaller readers on identical packets. Do not optimize cost before locating the source of errors.

Deliver Resume and an on-demand digest in the existing client, with evidence expansion and correction feedback. Begin with a configured project list and explicit watch rules.

Exit when the baseline answers the initial held-out set, the user can resume a real interrupted task, and a correction persists after reindex. Record the quality, latency, and cost baseline before introducing Graphiti.

## Milestone 3 — Graphiti foundation spike

Select a released Graphiti version and one backend supported in the environment. The research commit is a source reference, not a recommendation to deploy untested main. Pin the SDK, backend, model interfaces, and embedding model/dimension.

Build the adapter behind the retrieval interface. Ingest source-backed units with stable IDs and explicitly scoped previous episodes. Keep sequential writes per partition initially. Resolve returned nodes/edges to canonical IDs and evidence before use.

The spike must demonstrate:

- Ingestion, search, restart, retry, and replay with the chosen backend/provider.
- Same-thread context without unrelated episode leakage.
- Correct treatment of promises, deadlines, unknown dates, and out-of-order evidence.
- Conservative identity resolution, reversible mistaken merges, and no authority transfer from extracted edges.
- Correct source mapping and temporal filter behavior on all query paths used.
- Deletion/correction propagation, including a failed summary rebuild and a clean projection reconstruction.

Compare against the baseline using the same reader and evidence budget. Adopt Graphiti only if its benefit is material for linked or temporal questions and its operations remain manageable. Otherwise keep the adapter boundary and continue without it.

## Milestone 4 — Attention and continuity pilot

Add the second source connector and connect records about the same work. Implement explicit ranking reasons, coalescing, snooze/dismiss semantics, quiet periods, and stale-source behavior.

Replay events before enabling any notifications. Then run an on-demand or digest-only pilot for two weeks. Record useful catches, missed important events, resumption successes, repeated alerts, and maintenance time. Do not infer success from click-through rate alone.

Exit when hard invariants pass and the pilot meets the agreed burden and usefulness criteria. Proactive delivery is an explicit later user configuration; automatic work dispatch remains disabled.

## Milestone 5 — Reflection and GraphRAG experiment

Add versioned developmental goals and a retrospective query path. First compare simple per-project/per-period summaries with direct evidence retrieval. Include counterexamples, contribution attribution, and archive coverage.

Only then export an authorized temporal snapshot to GraphRAG's custom-graph pipeline. Validate exact table schemas and citation round trips. Produce community reports in a background job and label their generation/time cutoff.

Compare global and, if justified, DRIFT queries against the simpler summary baseline. Final claims still require source evidence. Test correction and access-change invalidation of reports.

Exit when broad questions improve on held-out cases enough to justify extra indexing and reconstruction cost. A compelling graph visualization is not an adoption gate.

## Milestone 6 — Optional writes and wider scope

Add external action preparation, authorization, conditional execution, reconciliation, and verified receipts only after the read-only pilot works. Start with a narrow action such as proposing a status reconciliation, not autonomous delegation.

Test stale revisions, timeout after success, retries, revoked authority, and self-generated events. Make the actual change inspectable and use the designated source of truth. Do not create duplicate task records for convenience.

Multi-user operation, shared summaries, additional source types, and a separate personal-project deployment each require their own scope and evaluation decision. Growing the archive is not automatically the next best milestone.

## Suggested implementation boundaries

```text
connectors/       source-specific read capabilities and optional write adapters
archive/          retained payloads, revision identities, evidence spans
ledger/           entities, claims, work references, user direction, corrections
processing/       normalization, extraction, episode assembly, derivations
retrieval/        baseline engine and optional Graphiti/GraphRAG adapters
policy/           authorization, authority, time modes, attention eligibility
service/          client API, context assembly, receipts, health
evaluation/       private corpus adapters, replay, rubrics, comparison receipts
```

This is a suggested module layout, not scaffolding already present in this repository. Prefer one process and durable jobs until measured constraints require more services. Avoid starting with multiple coordinating agents or an autonomous ontology-maintenance loop.

## Cost and sizing worksheet

Measure events per day, normalized tokens per event, extraction context expansion, model calls per event, retry fraction, embedding volume, queries per day, evidence tokens per query, and full/partial rebuild frequency.

Estimate daily model usage from observed input/output tokens by stage and the approved provider's actual rates. Add graph database/storage costs and operator maintenance. Benchmark a small representative import before backfilling months of history. Batch reflection has different latency needs from an interactive Resume view.

Cache extraction by source revision, prompt/model version, and context hash. A change in context or authority policy can invalidate outputs even when the source text is unchanged. Do not cache authorized answers across principals without a proven scope-equivalence rule.

## Open decisions

The client extension mechanism, first source pair, designated authority homes, storage location, permitted model providers, retention requirements, and useful alert criteria must be resolved in the target environment. The generic design does not depend on a specific answer, but implementation acceptance does.

The first review should ask: can the assistant show one real commitment, explain its state from evidence, preserve where work stopped, and accept a correction without creating more work? That is the smallest complete product slice.
