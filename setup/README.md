# Set up the workflow with your agent

Follow **examples → approved rubric → connect Jev → saved review**. Use an existing approved rubric as the starting point. Do the technical work; keep the reader's choices about judgment, source scope and review.

## 1. Start with examples

Check Python 3.11+, file access, existing email connectors and a review surface. Use an existing supported runtime; do not install tools or connect accounts automatically. With no connector, offer a pasted sample or the fictional demo. Without a native review surface, use local HTML or numbered chat.

Follow the [Gmail notes](gmail.md) to confirm the account and a small read-only scope. Read complete conversations and relevant sent replies and attachments. Explain that ordinary source stays in memory, private metadata stays in ignored `local/`, and host transcripts may retain reads. Saving full teaching examples needs separate approval.

## 2. Review the rubric

Use just three categories:

- **Needs action:** an unfinished reply, task or decision for the reader, urgent or not.
- **Worth seeing:** no action needed, but wanted reading or an update that affects plans or understanding.
- **Skip:** neither. Recommend skipping, but still show it for the reader to confirm. Do not alter the inbox or make future-mail rules.

Visualize definitions with gold and anti-gold examples when the host supports it; otherwise show a compact table. Probe an unresolved request versus its resolved thread; an unwanted invitation versus an agreed commitment; and a useful update versus routine acknowledgment. Keep timing separate from the category. Missing substantive context gets an uncertainty flag; incomplete retrieval stays on hold.

Start from [the rubric](../rubric/rubric.json) and [gold/anti-gold examples](../rubric/examples.json). Approve and [save the rubric and teaching examples](../workflow/docs/agent-reference.md#save-approved-configuration). Your approved copies live in `local/my-review/rubric.json` and `local/my-review/references.json`. Keep the library small. Do not automatically copy personal preferences or turn review history into teaching data.

## 3. Connect Jev

Follow [Jev setup](jev.md). Copy [.env.example](../.env.example) to `.env` at the repository root and enter the TypeSafe key locally. Keep it outside chat and Git. Start with a fictional email; then confirm the small real-email scope and that full messages, context and approved examples will go to TypeSafe. Use the fixed Jev evaluator identity and the saved rubric for both tests and the actual workflow.

If Jev is unavailable, pause this path. A fictional demo or explicitly chosen coding-agent alternative is fine, but do not silently substitute it and claim Jev worked.

## 4. Review a first run

Pass fresh complete conversations to `workflow/pipeline.py` through stdin, using the saved rubric, references and agreed request bound. Run the [command below](#command-for-the-agent) from the repository root. It prepares the requests, calls Jev, checks and saves the results, and generates the review. All requested decisions must validate before a batch is saved. Saved successful attempts can be reused after an interrupted batch; failed or uncertain attempts are never automatically resent.

Show all categories, uncertainties, holds and original links. Jev does not write reasons: the default review text is explicitly a category definition. If the reader asks why, inspect the original and identify your explanation as the coding agent's interpretation.

Use [review display and receipts](../workflow/docs/inline-review.md). Save each submitted correction, acknowledgment or follow-up instruction and read back its receipt. An unchanged rerun should preserve those choices without another Jev call. After a correction, [discuss whether the rubric should change](../workflow/docs/agent-reference.md#improve-the-rubric-with-the-reader), even without a rubric-update request. **Use to update rubric** asks for a rule-change proposal, not full-source retention. Offer a rubric tweak, a teaching example or both. Show exact proposed wording and get approval before saving it. Full teaching examples need separate approval. Test an approved change on a fresh similar case plus a contrast; never claim a cached rerun proves learning.

Follow-up notes authorize the specified work; classification alone does not. Sending, changing accounts and scheduling require their corresponding user instruction.

## 5. Finish setup

Confirm scope, actual Jev results, review delivery, saved receipt and unchanged rerun. Leave one item untouched and verify it resurfaces while a saved clear/assignment/correction stays quiet. If using Remind me, verify it returns next review or at the first review after the custom time; it creates no separate notification. Showing the review is not acknowledgment, and unchanged items reuse their saved classification. Name remaining gaps. Keep live model evidence separate from simulated code tests and reader acceptance.

Stop before creating a schedule unless explicitly asked. [Scheduling](../workflow/docs/scheduling.md) · [Technical reference](../workflow/docs/agent-reference.md) · [Rubric pressure test](../workflow/docs/rubric-check.md).

## Command for the agent

Stream the connector's normalized input through stdin; do not save ordinary email bodies to a file:

```sh
python3 workflow/pipeline.py --root local/my-review --env-file .env --live --max-requests 5
```

The command expects stdin; it does not fetch Gmail itself. Use the input shape in `workflow/demo/inputs.json`, adapted to the authorized account. A cap of 5 allows at most five new classifications; choose a cap matching the agreed batch. Without `--live`, it prepares and previews without calling Jev. An unchanged rerun reuses saved decisions.
