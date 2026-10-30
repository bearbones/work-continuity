# Research and foundation choices

## Recommendation

Build the source archive, canonical ledger, authority policy, and evaluation harness independently of any memory framework. Compare a simple hybrid retrieval baseline with a Graphiti-backed projection on the same corpus. Add GraphRAG community summarization only if broad retrospective questions benefit enough to justify its additional processing and maintenance.

This is a proposed architecture, not a result demonstrated by the papers below. Published findings establish useful mechanisms and evaluation ideas; they do not establish reliability for niche technical work, correct task completion, or reduced coordination burden.

## Research to design mapping

| Foundation | Mechanism established by the source | Proposed use here | What still belongs to the application |
| --- | --- | --- | --- |
| RAPTOR | Recursive clustering and summarization; retrieval across abstraction levels | Multiscale navigation and an optional summary-retrieval experiment | Evidence validity, updates, permissions, and correction propagation |
| Microsoft GraphRAG | Entity relationships, hierarchical communities, community reports, local/global retrieval | Broad project and developmental retrospectives | Authoritative work state, time semantics, attention policy, and client behavior |
| Zep research | Episodic, semantic, and community graph layers; temporal facts and hybrid retrieval | Temporal-memory design reference | Full revision history and application-specific authority |
| Graphiti library | Incremental episode processing, typed graph objects, configurable search | Optional live memory projection | Source archive, ledger, integration policy, and tested recovery |
| LongMemEval | Evaluates extraction, cross-session reasoning, updates, time reasoning, and abstention | Evaluation categories and separation of indexing/retrieval/reading failures | Workplace-specific fixtures and measured user burden |

The distinction between **Zep**, the service/research system, and **Graphiti**, the open-source library, matters. They are not interchangeable deployments. This design proposes an optional self-hosted Graphiti adapter and does not assume feature parity with a hosted Zep product.

## RAPTOR and the pyramid intuition

RAPTOR recursively groups and summarizes text, forming a tree of abstraction levels. It evaluates both tree traversal and searching across the collapsed set of nodes. This supports using summaries to retrieve broader context rather than limiting retrieval to nearby text chunks. Its document QA results do not establish that recursive summaries remain correct under edits, conflicting sources, or continuous work updates. [RAPTOR, methods and retrieval experiments](https://arxiv.org/html/2401.18059v1)

**Design inference:** keep the pyramid as a navigation projection with direct leaf search. Begin with explicit project and episode groupings; only add learned clustering if it improves recall. The application will version summaries, retain their input dependencies, and invalidate affected ancestors after corrections. These are proposed lifecycle rules, not claims about RAPTOR's implementation.

## Microsoft GraphRAG

### Mechanisms to borrow

The GraphRAG paper constructs a graph from extracted entities and relationships, partitions it into hierarchical communities, and summarizes those communities. Its focus is query-focused summarization over a corpus, including global questions poorly served by retrieving a few similar passages. Its evaluation includes LLM-based relative judgments; those results should not be interpreted as calibrated factual correctness or proof of practical value in this product. [GraphRAG paper, methods and evaluation](https://arxiv.org/html/2404.16130v2)

The documented indexing pipeline extracts entities, relationships and claims, detects communities, generates reports, and produces embeddings. It stores tabular outputs as Parquet by default and embeddings in a configured vector store. [Indexing overview](https://microsoft.github.io/graphrag/index/overview/)

Local search begins with query-relevant entities, follows their relationships and mappings to reports and source text, and assembles a bounded context. That is a useful model for a resumption packet that joins a work item to its decision and implementation evidence. [Local search](https://microsoft.github.io/graphrag/query/local_search/)

Global search uses community reports at a chosen hierarchy level, generates intermediate answers over report batches, and reduces selected points into a final answer. More detailed levels can require more processing. This fits broad reflective questions better than the event-by-event notification path. [Global search](https://microsoft.github.io/graphrag/query/global_search/)

DRIFT incorporates community context into local exploration and follow-up questions. It is a candidate for questions whose relevant entities are initially unclear, but should be evaluated against a simpler bounded expansion before adding it. [DRIFT search](https://microsoft.github.io/graphrag/query/drift_search/)

### Direct integration path

GraphRAG documents a bring-your-own-graph path using entity, relationship, and optionally text-unit tables. The minimal report workflow uses `create_communities` and `create_community_reports`; local and other retrieval modes also require text units and relevant embeddings. This provides a route to reuse the application's accepted graph projection without independently re-extracting the same entities. [Custom graphs](https://microsoft.github.io/graphrag/index/byog/)

The proposed adapter exports one authorized, temporally defined snapshot:

| Application object | Export role |
| --- | --- |
| Stable entity ID, name, scoped description | Entity row |
| Selected typed relationship, endpoints, description | Relationship row |
| Permitted source passage and immutable evidence ID | Text-unit row |
| Export generation, scope, time interval, knowledge cutoff, policy version | Application manifest beside the tables |

Before exporting, resolve field authority, apply current permissions, select claim revisions for the requested time mode, and remove rejected or stale derived content. Do not silently flatten an ownership history into simultaneous current owners. A historical report may include transitions if its descriptions preserve dates and attribution.

Relationship weight is a documented clustering input. The application must define it deliberately; it is not a confidence probability or priority score. The initial export can use uniform weights for accepted explicit links and evaluate alternate weighting separately.

The adapter is responsible for checking exact schemas against the chosen library version. Validate endpoint identity conventions, required columns, text mappings, embedding requirements, and one full export/query round trip. A generic graph export or a list of triples is not automatically GraphRAG-compatible.

Reports remain derived text. Map report citations back to the application manifest and evidence passages, and perform final source-grounded synthesis in the application. Build snapshots asynchronously, with explicit watermarks. Do not assume Graphiti output can be passed directly to GraphRAG or that a GraphRAG report honors the application's historical and authorization rules automatically.

## Zep and Graphiti

### Research contribution

The Zep paper describes episodes linked to semantic entities and relationships, with communities above them. It separates system recording time from the period when a fact applies, and combines semantic, lexical, and graph retrieval with reranking. It also describes LLM-driven contradiction handling that favors newer information when invalidating edges. Its benchmarks concern memory retrieval and answering, not task authority or notification usefulness. [Zep paper, sections 2–4](https://arxiv.org/html/2501.13956v1)

**Design inference:** reuse incremental temporal associations, but put field authority and uncertainty outside automatic edge invalidation. A recent casual comment must not override a tracker's lifecycle or an explicit user goal simply because it arrived later. Preserve the independent ledger so conflicting interpretations can be recovered and audited.

### Source inspection snapshot

The following implementation details were inspected at Graphiti commit [`72b5c59c06607e09ea855be61b6ff5a3446fc951`](https://github.com/getzep/graphiti/tree/72b5c59c06607e09ea855be61b6ff5a3446fc951). This is a research reference, not a tested deployment pin. The repository metadata at this commit declares `graphiti-core` version `0.31.2`. [Package metadata](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/pyproject.toml)

The public repository documents multiple graph backends and warns that structured-output capability affects extraction reliability, particularly with smaller models. Select and test one backend/provider combination rather than assuming identical behavior across combinations. [Graphiti repository](https://github.com/getzep/graphiti)

### Ingestion adapter

The inspected `Graphiti.add_episode` accepts a body, source type, reference time, optional UUID and group, typed entities/edges, extraction instructions, and explicitly selected previous episodes. Its implementation documentation recommends sequential episode ingestion. When previous episode IDs are omitted, recent episodes can supply context. [Ingestion API](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/graphiti_core/graphiti.py#L1334)

Proposed adapter behavior:

1. Ingest a source-backed unit with author, role, thread, timestamps, and evidence IDs; keep raw authoritative storage in the application.
2. Derive a stable UUID from partition, source identity, source revision, segment, and projection generation. An edited message gets a new revision mapping.
3. Supply only same-thread or explicitly related previous episode IDs. Passing no context is preferable to importing unrelated conversations.
4. Serialize writes within each graph partition in the first adapter. Test bulk/backfill equivalence before enabling faster import modes.
5. Treat extraction outputs as proposed associations. Persist their mapping to source revisions and apply application policy before presenting them as accepted state.
6. Keep update receipts and projection checkpoints; a successful SDK return alone is not proof that all application-level postconditions hold.

A project partition is not automatically an access boundary. Initially use separate deployments for work and personal material, and homogeneous authorized scopes for graph ingestion. Broader access patterns require tested authorization across graph traversal and derived summaries.

### Temporal representation

`EntityEdge` includes evidence episode IDs plus `created_at`, `expired_at`, `valid_at`, `invalid_at`, and, at the inspected revision, `reference_time`. Its field descriptions distinguish the time a promise becomes a fact from the future promised event, and distinguish soft deadlines from invalidation. [Edge model](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/graphiti_core/edges.py#L263)

Map these fields into application claims carefully. They do not establish that every historical mutation is stored as an immutable version. In particular, reconstructing “what the assistant knew then” requires the application's revision ledger or a replayed historical projection; four timestamps alone are insufficient proof of that capability.

The application's `due_at` stays separate. Unknown time, uncertain intervals, source authority, reported versus inferred status, and correction overrides remain application metadata even when the backend supports typed attributes.

### Retrieval adapter

At the inspected revision, `search()` returns entity edges, while `search_()` provides configurable graph-object results. The adapter should use the richer path when it needs episodes, entities, communities, and their mappings, then resolve every returned item to the canonical ledger. [Search entry points](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/graphiti_core/graphiti.py#L1913)

Search configuration includes cosine similarity, BM25, breadth-first expansion, and rerankers including reciprocal rank fusion, graph distance, MMR, and cross-encoding. Not every object type supports every method: episode search in the inspected configuration is BM25. [Search configuration](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/graphiti_core/search/search_config.py)

Explicit temporal filters are represented for edge validity, invalidity, creation, and expiry, along with type and endpoint filters. Their existence does not prove every backend and query path enforces the application's desired interval semantics. Test unknown dates, interval boundaries, and old knowledge cutoffs directly. [Search filters](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/graphiti_core/search/search_filters.py)

Use authorized partitions before candidate generation, then apply canonical state and provenance checks. Postfiltering alone is inadequate if forbidden text already influenced a reranker, summary, or model prompt. When a mixed graph cannot provide that guarantee, rebuild a narrower authorized projection.

### Removal and rebuilding

The inspected `remove_episode` removes support links, preserves edges supported by other episodes, and attempts to rebuild surviving entity summaries. Its error path can retain an old summary if rebuilding fails. Therefore an SDK deletion call is not an application-wide erasure receipt. [Removal implementation](https://github.com/getzep/graphiti/blob/72b5c59c06607e09ea855be61b6ff5a3446fc951/graphiti_core/graphiti.py#L2174)

Maintain a deletion quarantine at the application boundary. Verify absence from graph results, raw passages, embeddings, topic reports, context caches, and pending notifications. If rebuild verification fails, keep the affected scope unavailable or rebuild the projection from retained authorized sources. The canonical ledger's dependency graph controls this workflow.

## Evaluation research

LongMemEval separates information extraction, multi-session reasoning, knowledge updates, temporal reasoning, and abstention. It also distinguishes indexing, retrieval, and reading choices, and shows that correct retrieval does not eliminate reading failures. These are useful categories for diagnosing a smaller model independently of memory quality. [LongMemEval](https://arxiv.org/html/2410.10813v1)

The proposed evaluation adds authoritative state, source corrections, identity collisions, deletion, access boundaries, and notification burden. Those are product requirements rather than claims covered by the benchmark. See the [evaluation plan](evaluation.md).

## Choice and adoption gates

| Option | Why choose it | Main cost or uncertainty | Adoption gate |
| --- | --- | --- | --- |
| Ledger plus hybrid retrieval and explicit adjacency | Few moving parts, understandable authority and replay | Custom entity/episode linking | Baseline for every experiment |
| Add Graphiti | Reuse incremental semantic extraction and graph retrieval | Model-dependent extraction, graph operations, reconciliation | Better linked/temporal answers at acceptable cost, with invariants preserved |
| Add GraphRAG snapshots | Reuse corpus-level community summarization | Batch cost, stale reports, export/schema work | Better broad reflection than simple project/time summaries |
| Add both | Different tools for live memory and retrospective views | Two projections and more invalidation paths | Each independently clears its gate; combined replay and erasure remain correct |
| Hosted memory service | Potentially less infrastructure to operate | Target-environment data handling and API fit | Separate workplace decision; not required by this design |

GraphRAG source was inspected at [`c600ff80b77b9b62c47d539a3ac9569e95d8949b`](https://github.com/microsoft/graphrag/tree/c600ff80b77b9b62c47d539a3ac9569e95d8949b), including its [custom graph guide](https://github.com/microsoft/graphrag/blob/c600ff80b77b9b62c47d539a3ac9569e95d8949b/docs/index/byog.md). Its top-level workspace metadata is not a release version. Select a released version and pin dependencies during the implementation spike; this document does not claim installation or runtime verification of either library.
