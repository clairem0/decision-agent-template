# Set up the workflow with your agent

Follow the article: **explore examples → approve the rubric → test and review → optionally schedule or add Jev**. Start with the coding agent as classifier unless the reader has already chosen Jev. Preserve an existing approved rubric and classifier choice. Do the technical work; keep the reader's choices about judgment, source scope and review.

Follow the reader's current prompt. If they ask to download or explain the template, briefly orient them and stop there. If they ask for the fictional demo, show it and stop there. During setup, pause for their judgments and rubric approval; do not jump ahead to keys, scheduling or a large inbox run.

Want to try Jev without personal data? Use the [50-thread synthetic inbox](../workflow/README.md#try-jev-without-gmail). That path does not require Gmail, personal context or the setup steps below; finish there unless the reader asks to connect their own inbox.

## 1. Explore examples together

Check Python 3.11+, file access, existing email connectors and a review surface. Use an existing supported runtime; do not install tools or connect accounts automatically. Without a native review surface, use local HTML or numbered chat.

- **Connected email:** follow the [Gmail notes](gmail.md) to confirm the account and a small read-only scope. Read complete conversations, including relevant sent replies and attachments.
- **No connected email:** use the [pasted-sample path](gmail.md#without-an-email-connection), or show the fictional demo if the reader wants to explore without personal data. Do not require a connector or API key to continue.

Discuss a small batch with the reader. Offer preliminary categories and ask what they would change; explore another batch if needed. Look at sender, content, obligations and later replies together. Treat these as discovery, not an approved rubric or permission to save full teaching examples. Explain that ordinary source stays in memory by default, private metadata stays in ignored `local/`, and host transcripts may retain reads.

## 2. Make and approve the rubric

Use just three categories:

- **Needs action:** an unfinished reply, task or decision for the reader, urgent or not.
- **Worth seeing:** no action needed, but wanted reading or an update that affects plans or understanding.
- **Skip:** neither. Recommend skipping, but still show it for the reader to confirm. Do not alter the inbox or make future-mail rules.

When the reader is ready, draft the rubric from the examples and their feedback. Show an easy-to-scan reference sheet with **three horizontal rows** and columns **Category / Belongs here / Goes elsewhere**. Use concrete examples and contrasts; the latter two columns are the gold/anti-gold teaching pattern. Use a compact table if visualization is unavailable.

Probe an unresolved request versus its resolved thread; an unwanted invitation versus an agreed commitment; and a useful update versus routine acknowledgment. Keep timing separate from category. Missing substantive context gets an uncertainty flag; incomplete retrieval stays on hold.

Use [the starter rubric](../rubric/rubric.json) and [teaching examples](../rubric/examples.json) as shapes, not assumed personal preferences. Get approval for the rubric and separately for any full examples retained, then [save the approved configuration](../workflow/docs/agent-reference.md#save-approved-configuration). Use `{"references":[]}` if no examples are approved for storage. Keep the library small and do not automatically turn review history into teaching data.

## 3. Review a first run

Use a small agreed fresh sample, such as yesterday's conversations or a new pasted batch. Record the source scope accurately: pasted samples cannot establish coverage of the reader's inbox.

**Without Jev (the starting path):** follow [Classify without Jev](../workflow/docs/agent-reference.md#classify-without-jev). Prepare full inputs with the saved rubric and examples, classify them with the actual available coding agent, validate and save the answers, then render the review. No TypeSafe key, API setup or Jev command is needed. This is a fresh classification, unlike the demo's fixed simulated judgments.

**If the reader has chosen Jev:** follow [Jev setup](jev.md) and the [pipeline command](#command-for-jev). Each valid decision is saved independently; failed calls stay pending while successful results remain reviewable. Saved successful attempts can be reused after interruption, and failed or uncertain attempts are never automatically resent. A successful answer with an evidence flag is reviewable, including Skip. Jev supplies no written reasons; label its category definitions and identify any additional explanation as the coding agent's interpretation.

Show all categories, uncertainties, holds and verified original links using [review display and receipts](../workflow/docs/inline-review.md). Explain **Send changes to chat**; if a native bridge is unavailable, use copy-to-chat or the numbered fallback. Save submitted choices and read back their receipts. An unchanged rerun should preserve choices without another classification.

After a correction, [discuss whether the rubric should change](../workflow/docs/agent-reference.md#improve-the-rubric-with-the-reader), even without a rubric-update request. **Use to update rubric** asks for a rule-change proposal, not full-source retention. Offer a rubric tweak, a teaching example or both. Show exact proposed wording and get approval before saving it. Full teaching examples need separate approval. Test an approved change on a fresh similar case plus a contrast; a cached rerun does not prove learning.

Follow-up notes authorize the specified work; classification alone does not. Sending, changing accounts and scheduling require their corresponding user instruction.

## 4. Finish the manual setup

Confirm source scope, which classifier actually ran, review delivery, a saved receipt and an unchanged rerun. Leave one item untouched and verify it resurfaces while a saved clear/assignment/correction stays quiet. If using Remind me, verify it returns next review or at the first review after the custom time; it creates no separate notification. Showing the review is not acknowledgment. Name remaining gaps and distinguish fresh model judgment, simulated checks and reader acceptance.

Stop here unless the reader asks for more. For a daily workflow, follow [scheduling](../workflow/docs/scheduling.md) with the existing classifier and a source that will be available at runtime. Pasted samples alone do not provide fresh inbox access.

## 5. Add Jev when requested

Follow [Jev setup](jev.md). Keep the reader's approved rubric, examples, state history and review interface. Help them create `.env` from [.env.example](../.env.example) and open it for local key entry; keep the key outside chat and Git. Test one fictional email in a separate test root, then agree on a small real-email or pasted batch and explain that full content, relevant context and approved examples go to TypeSafe. Do not treat the API test as proof of the Gmail handoff.

Switching classifiers changes the evaluator contract, so fresh inputs need reassessment; do not relabel old coding-agent results as Jev results or discard their history. If the reader asks to classify the bundled fake inbox with Jev, use the separate synthetic path above with its own fictional rubric. If Jev is unavailable, pause that path and offer continuing with the coding agent; never silently substitute it and claim Jev worked.

## Command for Jev

Only for the chosen Jev path, stream normalized input through stdin without saving email bodies to a file:

```sh
python3 workflow/pipeline.py --root local/my-review --env-file .env --live --max-requests 5
```

The command expects stdin; it does not fetch Gmail itself. Use the input shape in `workflow/demo/inputs.json`, adapted to the agreed source. If the host makes stdin transfer difficult, use the [reader-approved temporary-file option](gmail.md#hand-complete-conversations-to-jev). A cap of 5 allows at most five new classifications; choose a cap matching the agreed batch. Without `--live`, it prepares and previews without calling Jev. An unchanged rerun reuses saved decisions.
