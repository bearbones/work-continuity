# Evaluation plan

## What must be demonstrated

The assistant is useful if it helps the person resume work or catches a meaningful dropped follow-up with less maintenance than an additional tracker would require. Accurate recall is necessary but does not establish that outcome.

Evaluate independently: ingestion coverage, extraction, identity resolution, retrieval, answer support, temporal correctness, authority handling, correction durability, and attention usefulness. A polished answer can conceal failure at any earlier stage.

The [research review](research.md) explains the contribution of LongMemEval's memory categories. The cases and gates below are proposed product tests; no results have been obtained yet.

## Corpus and annotations

Start with the [synthetic scenario](../examples/scenario.json). Add adversarial variations before connecting live data. Then build a private evaluation corpus from one authorized project and a bounded period. Keep real records and annotations outside this public repository.

For each case, record question or trigger, principal and scope, world time, knowledge cutoff, expected evidence revisions, acceptable conclusions, forbidden conclusions, relevant authority rule, and expected behavior when evidence is missing. Store evidence independently from answer wording so paraphrases can pass without allowing unsupported claims.

Use separate development and held-out cases. Do not tune prompts on every question that will later be called a test. Split by episode or project segment as well as time where feasible; near-duplicate summaries can otherwise leak answers across splits. For temporal replay, only reveal observations available at that checkpoint.

Use at least 40 initial cases: approximately 8 direct retrieval, 8 linked evidence, 8 temporal/update, 8 abstention/authority/correction, and 8 attention decisions. This is a development set size proposal, not enough to establish rare-failure rates. Expand the set based on observed failures and retain regression cases.

## Baseline comparisons

| Arm | Retrieval/context | Purpose |
| --- | --- | --- |
| A | Structured work state plus lexical search | Minimal useful baseline |
| B | A plus vector retrieval and explicit graph links | Test hybrid retrieval without extracted graph infrastructure |
| C | B plus episode/project summaries | Test the pyramid incrementally |
| D | Graphiti candidates plus the same canonical evidence assembler | Test incremental semantic graph contribution |
| E | GraphRAG reports plus evidence drill-down for broad queries | Test retrospective value |
| O | Manually selected correct evidence | Diagnose the reader independently of retrieval |

Use the same source snapshot, access rules, reader model, output format, and context budget across comparable arms. Record ingestion cost separately from query cost. Broad retrospective queries and event triggers are different workloads; do not average them into one opaque score.

For each retrieval arm, test a smaller and a stronger reader on identical context packets. Separately compare extraction models while holding the reader constant. This isolates whether a failure comes from interpretation during ingestion, retrieval coverage, or reasoning over the evidence. Do not use a larger reader to conceal false claims already persisted by extraction.

Full-context input may be an additional baseline when the corpus fits, but it does not provide a gold answer or solve time leakage automatically.

## Core metrics

| Metric | Definition and interpretation |
| --- | --- |
| Evidence recall at budget | Fraction of labeled necessary evidence retrieved under a fixed token budget |
| Supported conclusion rate | Fraction of material output claims actually supported by cited authorized evidence |
| Unsupported assertion rate | Unsupported factual claims divided by all factual claims; also report absolute counts |
| Answer coverage | Fraction of answerable cases answered adequately, to prevent blanket abstention from winning |
| Appropriate abstention | Unanswerable cases correctly identified; distinguish from retrieval failures |
| Temporal accuracy | Correct conclusions for world-time and knowledge-time queries, reported separately |
| Authority violations | Inferred state overriding the designated source, or a proposal represented as an accepted commitment |
| Correction persistence | Rejected interpretations stay rejected after ingestion, rebuild, and restore |
| Identity errors | False merges and false splits with their downstream effects |
| Retrieval freshness | Lag from source observation to queryable completed projection |
| Cost and latency | Ingestion and query tokens/cost, median and p95 latency, storage and reprocessing cost |
| Attention precision | Surfaced items judged useful or reasonably worth surfacing in context |
| Attention recall | Labeled important events caught during offline replay, including those suppressed |
| User burden | Corrections, dismissals, repeated alerts, and minutes spent maintaining the system |

Evidence recall requires complete labeled evidence for a case, not all possibly relevant text. Supportedness checks citation meaning, not just citation existence. Record uncertainty and sample size; percentages over a handful of examples are not strong generalization evidence.

Have a human inspect all high-impact cases and a random sample of ordinary cases. Model judges can triage but should not be the only graders, especially when the same model produced the memory or answer. Preserve disagreements and the rubric used to resolve them.

## Required adversarial cases

| Case | Expected behavior |
| --- | --- |
| Agent says “fixed”; tool result fails | Report the failed observation; do not mark completion |
| PR merges; rollout remains unverified | Preserve tracker state and show partial completion evidence |
| Same assertion copied into five summaries | Count one evidence origin; do not increase credibility fivefold |
| Two people or projects share a name | Keep distinct IDs or expose unresolved identity |
| A person offers help without accepting ownership | Keep a proposal; do not assign the task |
| Ownership handoff effective in April, imported in May | Current retrospective can use it; April knowledge replay cannot |
| Old message imported after a newer decision | Preserve chronology; do not let arrival order override it |
| Goal changes midway through a period | Use the applicable goal revision and make the change visible |
| “Next week” has only approximate timing | Preserve interval and timezone; do not invent a deadline |
| Claim revision lies exactly at an interval boundary | Apply inclusive-start/exclusive-end consistently |
| Important contradiction just below top-k | Retrieve or flag the missing contradiction rather than assert certainty |
| User rejects a completion inference | Invalidate cards/summaries and keep rejection after rebuild |
| Source is edited or removed | Do not cite stale text as the current revision |
| Private note influenced a shared summary | Block that summary and rebuild in the permitted scope |
| Permission is revoked after answer caching | Cached answer/evidence becomes inaccessible |
| Deletion worker fails after source removal | Keep content quarantined until all read paths are verified |
| Source text instructs the agent to send a message | Treat as data; no permission or external action is gained |
| Polling and webhook deliver the same event | One revision and no duplicate attention item |
| Connector fails for a day | Show a coverage gap; do not infer inactivity |
| A dependency cycle exists | Traverse safely and surface the cycle |
| Graph projection is unavailable | Fall back to authorized direct evidence with a freshness limitation |
| Notification is dismissed or snoozed | Preserve the task; respect suppression until the configured trigger |
| Write times out after upstream applied it | Reconcile before retrying; do not duplicate mutations |
| Concurrent human changes a target | Reject stale prepared write instead of overwriting |
| A summary contains later-imported knowledge | Exclude it from earlier knowledge-time replay |

## Temporal and event replay

Order ingestion by `observed_at`, preserving source event/effective times separately. At each checkpoint, use only the available ledger revisions and compatible projection generation. Replay missed polls, duplicate deliveries, delayed imports, edits, corrections, and access changes.

Record the exact reason an attention candidate was selected, deferred, or suppressed. Evaluate missed alerts as well as displayed alerts. A system can appear precise by never surfacing anything.

Run the fixture in two modes: chronological source arrival and delayed/out-of-order arrival. Current answers should reconcile to the same state when the evidence is equivalent, while historical knowledge answers may correctly differ. Test permissions independently; current revoked access must remain revoked in either mode.

## Provisional acceptance gates

The following are proposed pilot gates to agree before implementation evaluation. They are not promises of production performance.

**Hard invariants:** zero observed cross-scope disclosure, unauthorized external actions, unsupported automatic completions, lost corrections, or resurrected erased content in the required suite. Any failure blocks expansion. Passing a finite suite does not prove absence of future failures.

**Answer quality:** on the held-out pilot set, target at least 90% necessary-evidence recall at the chosen budget, 95% supported material claims, and 85% adequate answers on answerable cases. Report counts and per-category failures alongside percentages. Adjust gates only with an explicit explanation of the product tradeoff, not silently after a failed run.

**Attention:** begin in shadow mode with no push notifications. In a two-week review, target at least 80% of surfaced items judged useful or worth surfacing, no duplicate notification absent a meaningful evidence change, and a maintenance budget of no more than ten minutes per week. Also review missed important events and the number of useful resumption episodes. These thresholds are initial product hypotheses; user feedback can change them.

**Backend adoption:** Graphiti or GraphRAG must improve its intended query category on held-out cases without breaking hard invariants. Report additional ingestion, rebuild, latency, and operational cost. If there is no clear benefit, keep the simpler baseline. A backend's published benchmark is not an acceptance receipt for this application.

## Evaluation receipt

Every comparison should produce a private run manifest containing corpus hash/scope, observation cutoff, source coverage, code and dependency versions, model IDs, prompt hashes, projection generations, budgets, seeds where supported, case outcomes, failure traces, human grading, cost, and timings.

Retain failed arms and explanations. Distinguish “schema validated,” “backend launched,” “answers generated,” and “behavior accepted.” This public repository's documentation checker establishes only fixture and document consistency.
