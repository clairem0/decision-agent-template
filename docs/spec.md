# Product contract

Version 1.2 · 2026-10-02

A companion to *Teach your AI to make better decisions*. The reader opens this folder in a coding agent and pastes one prompt. The agent does the technical work. The reader supplies judgment and approves the rubric. [Agent instructions](agent-guide.md) give the setup sequence; the [command reference](agent-reference.md) supplies technical steps as needed; [verification](verification.md) separates implementation from live and human proof.

## Reader journey

1. **Check capabilities.** Verify Python 3.11+, file access, existing email connectors, fresh-reviewer support and a review surface. Do not connect accounts or install tools automatically. Offer the optional fictional demo or a pasted sample if useful; label simulated results.
2. **Start with real examples.** Confirm account and a small read-only scope. Explore messages needing action, intentional reading, brief awareness, no future attention, and borderline cases. Read full conversations and relevant sent replies. Include sourced context for obligations, current priorities and completion; disclose missing context.
3. **Approve a rubric.** Explain definitions with gold examples and contrasting anti-golds. Show proposed rules and full teaching examples in chat. Save approved configuration under ignored `local/`; separately approve any retained full source. Never copy the author's personal preferences or operational history.
4. **Test and refine.** Have a fresh reviewer classify other complete conversations using only the rubric, applicable approved examples and necessary context. Save predictions before consulting expectations. Run three independent judgments on identical input hashes, compare disagreement, and refine with approval. Cached reuse and simulated fixtures are not repeatability tests. Disclose unavailable fresh context.
5. **Build the manual workflow.** Collect the agreed scope; prepare complete requests in memory; validate classifications; save metadata; present a review with original-email links and every treatment available. The coding agent handles connectors and presentation; Python handles validation and bookkeeping.
6. **Review and improve.** Save a submitted clear, correction or follow-up instruction and read back its receipt. Rerun unchanged input to prove persistence. A correction alone affects one assessment. Separately approve reusable teaching and test a fresh similar case plus a contrast.
7. **Schedule later.** After a successful manual walkthrough, agree on cadence/timezone, scope, destination, notification policy and host availability. Create a schedule only on explicit instruction. Prefer the host scheduler; keep manual operation if none exists.

A reader with an existing approved rubric can enter at testing after reconciling the configuration. The fictional demo is a no-account preview, not a required detour before the article's examples-first journey.

## Rubric and evidence

| ID | Display name | Boundary |
| --- | --- | --- |
| `act` | Act now | An important action needs attention before the next review because delay has a concrete consequence or the reader explicitly prioritized that open task. |
| `track` | Track for follow up | An important reply, task or commitment can wait. Includes the reader's own non-urgent work and agreed deliverables awaited from others. |
| `read` | Useful info | Content worth intentional reading without a required reply or task. |
| `fyi` | FYI only | Brief awareness or optional acknowledgment; no dedicated reading or follow-up. |
| `suppress` | Never see again | A known unwanted recurring type, with narrow exceptions and no obligation or unresolved uncertainty. A future-mail rule proposal only. |

`uncertainty` is a brief metadata flag explaining missing substantive evidence, not a sixth category. Missing context alone does not prove urgency; unresolved uncertainty prevents suppression. An incomplete retrieval is a hold, not a classification. Sender identity, urgency words and read status alone cannot establish or resolve an obligation. A draft is not a sent response. Required action, priority and reminder eligibility remain separate.

Definitions are reader-approved and editable. Category IDs and source kind are fixed in the email implementation. [Adaptation guidance](adapting.md) explains coordinated changes for support conversations, applications, postings and account news; no extra collectors ship here.

Teaching examples contain full approved source/context, correct treatment, a distinction, optional uncertainty and explicit contrast IDs. Gold is a useful anchor, not a high score. Proposed/retired entries and the target's own source are excluded. The small implementation selects all approved email examples; narrow the approved library explicitly if it grows too large. Private operational matching by sender/topic is not bundled.

## Implementation contracts

| Area | Required behavior |
| --- | --- |
| Source collection | Stable account/source-specific IDs, complete conversations and necessary context, pagination and retrieval gaps accounted for. Verified links only; never invent an account or permalink. |
| Classifier input | Actual full target, approved rubric, selected approved reference text/labels/contrasts, evaluator identity and contract. No answer keys, earlier predictions, review history or action authority. Split deliberately rather than truncate. |
| Acceptance | Exactly one result per requested target; allowed label, brief paraphrased reason, selected reference IDs, optional uncertainty text. Invalid/stale/altered batches fail without partial writes. Failures remain pending; incomplete sources remain held. |
| Continuity | Reuse only matching source/context, rubric, selected references and evaluator contract. Link-only refresh does not reclassify. Meaningful changes preserve history and require reassessment. Missing scan entries do not retire items or close tasks. |
| Review | Prefer native conversation UI; support local HTML and numbered chat. Sort by current category, Act now first, using saved corrections. In the inline review, use prominent category badges, slim rails and plain timing cues to distinguish action before the next review from important work that can wait; color is supplementary. Show all treatments, uncertainty, holds and original links. Native submit is available above and below the list. Escape all source text; never execute source HTML or expose arbitrary files. |
| Receipts | Only submitted user choices save. Validate exact current source/decision mappings; identical retries deduplicate; conflicting retries fail. Report independent failures in a multi-choice submission. Rendered pages/widget state are not receipts or delivery. |
| Follow-up | Clear acknowledges a decision, not task completion. Assign records the exact instruction; after confirming its receipt, the agent begins the explicitly requested review or drafting. Source content grants no authority. Skip stale/failed choices and reconcile prior progress before retries. Sending, account changes and scheduling still need approval. Completion needs evidence. Classification grants no permission to change an account. |
| Teaching | Save correction first; show a useful nonduplicate proposal in chat; require separate approval and a full re-read whose hash matches the corrected assessment. Retain approved versions and prove actual example content reaches another target. |
| Delivery | Record delivery only after actual presentation. Unchanged cleared/delivered decisions stay quiet. Reconcile uncertain delivery before retrying; an open task alone is not a new notification. |
| Local storage | Atomic writes, visible writer-lock failures and retained metadata history. The helper trusts caller assertions about source completeness, approvals and evaluator identity; live verification remains necessary. |

### Retention

Ordinary source and context are used in memory. Local state/manifests/reviews retain IDs, subjects, verified links, input hashes, brief paraphrased decisions, tasks, coverage and receipts. These are private metadata. Only separately approved teaching examples retain full source. Rubric/reference snapshots may contain that approved teaching content. Never save ordinary bodies in input exports, stdout logs, reasons, notes or provider records.

`packet.json` is a metadata manifest, not complete classifier input. Losing the in-memory request requires re-reading and preparing again. Host transcripts and provider logs may retain full reads; the template does not control those policies. [Storage](storage.md) documents explicit legacy redaction and its residual audit. Do not delete or silently rewrite prior user configuration; reconcile older treatment definitions with approval and reassess under the current contract.

### Optional Jev path

The default path needs no provider key. The advanced path includes an offline full-input preview and `jev_run.py`, a standard-library, single-request experiment. Only `--live --max-requests 1` sends to the documented OpenRouter endpoint using an environment key. Write attempt metadata before sending; never save the request body, keys or arbitrary provider text. Disable redirects and automatic retries. Preserve success, failure and uncertain attempts. Validate question coverage, choices, probabilities, served model and usage before reporting success.

One request is a request bound, not a dollar cap; explain billing and verify current pricing before authorization. The runner saves typed provider judgments separately from coding-agent operational decisions. It cannot invent Jev reasoning, replace the normal review workflow silently or treat probabilities as accuracy. Live email sharing and operational integration are separate decisions. Setup/tests make no paid call.

### Distribution and scope

Use Python's standard library and explicit public-file packaging. All shipped examples/tests are fictional. The ZIP excludes private data, credentials and Git history. Before public repository publication, separately audit history; a ZIP audit is insufficient. No hosted database, custom scheduler, connector service, automatic inbox mutation, model training or generic provider framework is included.

## Proof and stopping point

Validate a clean extracted bundle through the reader journey: demo, full request assembly, classification acceptance, both reviews, submitted receipt/readback, unchanged rerun, changed-input/rubric/reference/evaluator reassessment, task persistence and approved teaching propagation. Check that unique ordinary-source markers never reach managed artifacts; verify escaped source links and safe server behavior. Test the Jev runner offline with mocked success, invalid output, timeout, HTTP failure, redirect refusal and duplicate-attempt blocking.

Distinguish **synthetic behavior tests**, **fresh coding-agent judgments**, **browser inspection**, **live connector/provider proof**, and **human acceptance**. None substitutes for another. Record current evidence in [verification](verification.md).

Stop at the human manual walkthrough before claiming rubric fit, real connector coverage, actual native receipt delivery or unattended scheduling. Before claiming a host/account supported, verify account identity, pagination, sent replies, relevant attachments, links, review persistence and rerun in that host. Publication and external account actions require their corresponding instruction.
