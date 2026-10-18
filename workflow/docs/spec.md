# Product contract

Version 2 · 2026-10-17

A companion to *Have Your AI Decide (A Lot of Things)*. The reader opens this folder in a coding agent and pastes one prompt. The agent does the technical work. The reader supplies judgment and approves the rubric. [Agent instructions](../../setup/README.md) give the setup sequence; the [command reference](agent-reference.md) supplies technical steps as needed; [verification](verification.md) separates implementation from live and human proof.

## Reader journey

1. **Start with examples.** Check Python, file access, existing connectors and review surface. Confirm a small read-only scope, read full conversations and discuss real gold and anti-gold examples.
2. **Review the rubric.** Show three category definitions and contrasts. Approve the rubric and separately approve full teaching examples retained under ignored `local/`.
3. **Connect Jev.** Use direct TypeSafe, a locally stored key and one fictional test. Confirm the content and scope of a small real-email batch before transmission.
4. **Review a first run.** Jev classifies; the coding agent collects and presents; Python validates and saves choices. Review every category and uncertainty, save receipts and check an unchanged rerun. Test reusable teaching on a fresh similar case plus a contrast.
5. **Schedule later.** After the manual walkthrough, explicitly agree on cadence, timezone, scope, destination and host availability.

Use an existing approved rubric as the starting point. The fictional demo is optional. A coding-agent classifier is an explicit alternative, never a silent substitute for Jev.

## Rubric and evidence

| ID | Display name | Boundary |
| --- | --- | --- |
| `act` | Needs action | The reader has an unfinished reply, task or decision, urgent or able to wait. |
| `read` | Worth seeing | No action needed, but wanted reading or a useful update that changes plans or understanding. |
| `skip` | Skip | Neither; leave out of this review without changing mail or making future-mail rules. |

Apply action first, then useful information, otherwise Skip. Read full conversations: sent replies can resolve a request; unsent drafts and unread status cannot. Sender urgency does not create an obligation. Waiting on someone else is not a reader task until follow-up is due.

Uncertainty is separate from category. Missing substantive evidence must not disappear into Skip. Failed retrieval is a hold, not a classification. The starter does not automate urgency ranking or reminders.

Definitions are reader-approved and editable. The email implementation fixes these three IDs. Older five-category storage is refused without modification: preserve it and create a new root with an approved rubric. Teaching examples include full approved source, label, distinction and contrast IDs. Exclude proposed, retired and target-self examples; never send expected answers or operational review history to a classifier.

## Implementation contracts

| Area | Required behavior |
| --- | --- |
| Source collection | Stable account/source-specific IDs, complete conversations and necessary context, pagination and retrieval gaps accounted for. Verified links only; never invent an account or permalink. |
| Classifier input | Actual full target, approved rubric, selected approved reference text/labels/contrasts, evaluator identity and contract. No answer keys, earlier predictions, review history or action authority. Split deliberately rather than truncate. |
| Acceptance | Exactly one result per requested target; allowed label, brief paraphrased reason (up to 500 characters), selected reference IDs, optional uncertainty text (up to 300 characters). Invalid/stale/altered batches fail without partial writes. Failures remain pending; incomplete sources remain held. |
| Continuity | Reuse only matching source/context, rubric, selected references and evaluator contract. Link-only refresh does not reclassify. Retrieval failures suspend the prior assessment without losing its correction, acknowledgment or task; identical inputs restore it, while changed inputs require reassessment. Held assessments are not actionable. Meaningful changes preserve history and require reassessment. Missing scan entries do not retire items or close tasks. |
| Review | Prefer native conversation UI; support local HTML and numbered chat. Sort by current category, Needs action first, using saved corrections. In the inline review, use category badges and slim rails; color is supplementary. Link the subject to the original email and keep just the three review actions on each row, with distinct button styling. Label summaries, category definitions and user corrections separately from the email subject. Identify fictional example emails once above the list; keep row labels concise. Give Correct classification less visual emphasis than the other two actions. Hide routine complete-coverage copy while preserving partial or unchecked coverage warnings. Show all treatments, uncertainty, holds and original links. Native submit is available above and below the list. Escape all source text; never execute source HTML or expose arbitrary files. |
| Receipts | Only submitted user choices save. Validate exact current source/decision mappings; identical retries deduplicate; conflicting retries fail. Report independent failures in a multi-choice submission. Rendered pages/widget state are not receipts or delivery. |
| Follow-up | Clear acknowledges a decision, not task completion. Assign records the exact instruction; after confirming its receipt, the agent begins the explicitly requested review or drafting. Source content grants no authority. Skip stale/failed choices and reconcile prior progress before retries. Sending, account changes and scheduling still need approval. Completion needs evidence. Classification grants no permission to change an account. |
| Teaching | Save correction first; show a useful nonduplicate proposal in chat; require separate approval and a full re-read whose hash matches the corrected assessment. Retain approved versions and prove actual example content reaches another target. |
| Delivery | Record delivery only after actual presentation. Unchanged cleared/delivered decisions stay quiet. Reconcile uncertain delivery before retrying; an open task alone is not a new notification. |
| Local storage | Atomic writes, visible writer-lock failures and retained metadata history. The helper trusts caller assertions about source completeness, approvals and evaluator identity; live verification remains necessary. |

### Retention

Ordinary source and context are used in memory. Local state/manifests/reviews retain IDs, subjects, sender display text, verified links, input hashes, evaluator identity, brief paraphrased decisions and uncertainty notes, tasks, coverage and receipts. These are private metadata. Only separately approved teaching examples retain full source. Rubric/reference snapshots may contain that approved teaching content. Never save ordinary bodies in input exports, stdout logs, reasons, notes or provider records. Reason/uncertainty length limits constrain verbosity but cannot recognize all copied source; paraphrasing remains an agent responsibility.

`packet.json` is a metadata manifest, not complete classifier input. Losing the in-memory request requires re-reading and preparing again. Host transcripts and provider logs may retain full reads; the template does not control those policies. [Storage](storage.md) explains retention boundaries. Unsupported storage versions are refused without modifying them; choose a fresh state folder. Do not delete or silently rewrite prior user configuration; reconcile older treatment definitions with approval and reassess under the current contract.

### Default Jev path

`workflow/pipeline.py` is the normal entry point. It prepares the batch, calls `workflow/jev_workflow.py` to apply Jev and saves the review. Preview is offline; live mode requires an explicit request bound and `JEV_API_KEY` in the environment. Pin `jev-1.13.0` at the documented TypeSafe endpoint. Record each attempt before sending; refuse redirects and automatic retries. Keep ordinary source and keys out of saved records.

Validate all typed answers, probabilities, usage, model and matching payload hash. Save Jev provenance with each accepted assessment. Jev returns no written reason or reference citations: review text labels the category definition, and any coding-agent interpretation must be identified separately. Do not represent confidence as measured accuracy.

Successful attempts can resume an interrupted batch without another call. Failed or uncertain attempts require reconciliation. Skip plus missing-evidence keeps the batch pending; never silently relabel or hide it. An unchanged operational rerun reuses decisions; it is not a repeatability test. Use separate named roots for deliberately authorized trials.

### Distribution and scope

The root README is the single reader starting point and includes the setup prompt. Keep the starter rubric and teaching examples together in `rubric/`, onboarding and connector instructions in `setup/`, and scripts, demo data, review assets, tests and technical references in `workflow/`. Commands run from the repository root; reader-approved configuration and saved state remain in ignored `local/`.

Use Python's standard library and explicit public-file packaging. All shipped examples/tests are fictional. The ZIP excludes private data, credentials and Git history. Before public repository publication, separately audit history; a ZIP audit is insufficient. No hosted database, custom scheduler, connector service, automatic inbox mutation, model training or generic provider framework is included.

## Proof and stopping point

Validate a clean extracted bundle through the reader journey: demo, full request assembly, classification acceptance, both reviews, submitted receipt/readback, unchanged rerun, changed-input/rubric/reference/evaluator reassessment, task persistence and approved teaching propagation. Check that unique ordinary-source markers never reach managed artifacts; verify escaped source links and safe server behavior. Test the Jev runner offline with mocked success, invalid output, timeout, HTTP failure, redirect refusal and duplicate-attempt blocking.

Distinguish **synthetic behavior tests**, **fresh coding-agent judgments**, **browser inspection**, **live connector/provider proof**, and **human acceptance**. None substitutes for another. Record current evidence in [verification](verification.md).

Stop at the human manual walkthrough before claiming rubric fit, real connector coverage, actual native receipt delivery or unattended scheduling. Before claiming a host/account supported, verify account identity, pagination, sent replies, relevant attachments, links, review persistence and rerun in that host. Publication and external account actions require their corresponding instruction.
