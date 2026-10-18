# What stays on disk

By default, ordinary full emails and retrieved conversation context remain at their original source, including the chat when the reader supplies a pasted sample. The agent reads them into memory for classification and passes their actual content, the rubric and approved teaching examples to the evaluator. It must not keep a local source export, save classifier stdout or put bodies in review pages, reasons, coverage notes or receipts.

The reader may explicitly approve a [temporary input file](../../setup/gmail.md#hand-complete-conversations-to-jev) for the Gmail-to-Jev handoff. Create only the agreed batch under the state root's `temporary-input/`, in a private, non-synced location. `pipeline.py --temporary-input PATH` reads and deletes the designated file before loading the key, preparing state or contacting Jev. Parsing errors also trigger deletion; a deletion failure stops processing. Confirm the file is gone after every run and clean up approved leftovers after startup failures or forced stops. This does not authorize retaining source, saving diagnostic output or teaching from it. File deletion is not secure erasure and cannot undo host transcripts or backups.

The starter saves source IDs, subjects, optional sender display text, verified original links, hashes of the evaluated input, rubric and approved-reference snapshots, brief paraphrased decisions, review choices, tasks, reminder times and coverage notes under ignored `local/`. These are still private metadata. Use neutral subjects if a subject itself contains sensitive information. Classifier reasons are limited to 500 characters and uncertainty notes to 300; these limits do not detect every copied excerpt. The agent must paraphrase, and user-entered notes may themselves contain sensitive text. Hashes establish equality, not recoverable source evidence.

The only full source retained after the handoff is a separately approved teaching example, including an approved anti-gold contrast. Gold is a teaching role, not necessarily a high-priority category. Previous approved versions may remain in reference history. Do not save full proposed examples: show the proposal in chat, then re-read the source after approval. The teaching helper checks the full source hash against the corrected assessment before writing the example. Correction alone stores only a decision and review receipt.

`prepare --stdin` returns the complete classifier batch to the agent on stdout. Its local `packet.json` is a **metadata manifest**, not that complete batch. `accept` validates results against this manifest and current state. Never classify from the saved manifest: retrieve source again and prepare again if the agent lost the in-memory batch. The helper does not read Gmail itself or verify a claimed complete capture. It trusts the agent's provenance and coverage.

Agent conversations, tool transcripts, host visualization storage and external provider logs may retain content the agent reads. This template controls its own files; it cannot promise that your coding agent never stores email. Check the host's data policy before a real run. A pasted sample also remains in that chat. If you choose Jev, the workflow sends full messages, relevant context, your rubric and approved examples to TypeSafe; agree on that scope before the first real run. Without Jev, classification stays with the coding-agent provider you are already using, subject to that host's data policy.

## Storage compatibility

Reminders are optional metadata on the current decision (`reminder.when` and, for timed reminders, `reminder.at`) plus the exact saved receipt. Text requests retain their original words, timezone and request timestamp in the receipt; `reminder_resolutions` records the agent-resolved time by receipt ID. Unresolved requests do not change state. Existing version-3 state needs no migration. Due checks never rewrite state; classification inputs exclude reminders.

Unsupported storage versions are refused without changing the existing folder. Preserve it and choose a fresh state root; do not copy ordinary source exports into the new workflow.

## Original-email links

Supply `original_url` only when the connector or a verified source-specific permalink supplies the original conversation in the correct account. The helper displays HTTPS links only, rejects executable URLs, credentials and control characters, and opens links with `noopener noreferrer`. A missing or unsafe link is omitted; the UI asks for a source re-read by ID instead. Links are display metadata and do not enter classifier input or cause reassessment on their own.

The demo's `mail.example.test` links are fictional illustrations and will not open a real mailbox.
