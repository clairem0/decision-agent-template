# Set up the reader's workflow

Follow **examples → approved rubric → connect Jev → saved review**. Use an existing approved rubric as the starting point. Do the technical work; keep the reader's choices about judgment, source scope and review.

## 1. Start with examples

Check Python 3.11+, file access, existing email connectors and a review surface. Use an existing supported runtime; do not install tools or connect accounts automatically. With no connector, offer a pasted sample or the fictional demo. Without a native review surface, use local HTML or numbered chat.

Confirm the account and a small read-only scope. Read complete conversations and relevant sent replies and attachments. Explain that ordinary source stays in memory, private metadata stays in ignored `local/`, and host transcripts may retain reads. Saving full teaching examples needs separate approval.

## 2. Review the rubric

Use just three categories:

- **Needs action:** an unfinished reply, task or decision for the reader, urgent or not.
- **Worth seeing:** no action needed, but wanted reading or an update that affects plans or understanding.
- **Skip:** neither. Leave out of this review; do not alter the inbox or make future-mail rules.

Visualize definitions with gold and anti-gold examples when the host supports it; otherwise show a compact table. Probe an unresolved request versus its resolved thread; an unwanted invitation versus an agreed commitment; and a useful update versus routine acknowledgment. Keep timing separate from the category. Missing substantive context gets an uncertainty flag; incomplete retrieval stays on hold.

Approve and [save the rubric and teaching examples](agent-reference.md#save-approved-configuration). Keep the library small. Do not automatically copy personal preferences or turn review history into teaching data. Older five-category state needs a new folder and an approved mapping, not an automatic rewrite.

## 3. Connect Jev

Follow [Jev setup](jev.md). Keep the credential outside chat and code. Start with a fictional email; then confirm the small real-email scope and that full messages, context and approved examples will go to TypeSafe. Use the fixed Jev evaluator identity and the saved rubric for both tests and the actual workflow.

If Jev is unavailable, pause this path. A fictional demo or explicitly chosen coding-agent alternative is fine, but do not silently substitute it and claim Jev worked.

## 4. Review a first run

Pass fresh complete conversations to `pipeline.py` through stdin, using the saved rubric, references and agreed request bound. Follow the command in [setup](../SETUP.md#command-for-the-agent). It prepares the requests, calls Jev, checks and saves the results, and generates the review. All requested decisions must validate before a batch is saved. Saved successful attempts can be reused after an interrupted batch; failed or uncertain attempts are never automatically resent.

Show all categories, uncertainties, holds and original links. Jev does not write reasons: the default review text is explicitly a category definition. If the reader asks why, inspect the original and identify your explanation as the coding agent's interpretation.

Use [review display and receipts](inline-review.md). Save each submitted correction, acknowledgment or follow-up instruction and read back its receipt. An unchanged rerun should preserve those choices without another Jev call. A correction affects this assessment. For broader improvement, separately approve a teaching example and test a fresh similar case plus a contrast. Never claim an unchanged cached rerun proves learning.

Follow-up notes authorize the specified work; classification alone does not. Sending, changing accounts and scheduling require their corresponding user instruction.

## 5. Finish setup

Confirm scope, actual Jev results, review delivery, saved receipt and unchanged rerun. Name remaining gaps. Keep live model evidence separate from simulated code tests and reader acceptance.

Stop before creating a schedule unless explicitly asked. [Scheduling](scheduling.md) · [Technical reference](agent-reference.md) · [Rubric pressure test](rubric-check.md).
