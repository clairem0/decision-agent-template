# What stays on disk

Ordinary full emails and retrieved conversation context stay in the source account. The agent reads them into memory for classification and passes their actual content, the rubric and approved teaching examples to the evaluator. It must not create a local source export, save classifier stdout or put bodies in review pages, reasons, coverage notes or receipts.

The starter saves source IDs, subjects, optional sender display text, verified original links, hashes of the evaluated input, rubric and approved-reference snapshots, brief paraphrased decisions, review choices, tasks and coverage notes under ignored `local/`. These are still private metadata. Use neutral subjects if a subject itself contains sensitive information. Classifier reasons are limited to 500 characters and uncertainty notes to 300; these limits do not detect every copied excerpt. The agent must paraphrase, and user-entered notes may themselves contain sensitive text. Hashes establish equality, not recoverable source evidence.

The only retained full source is a separately approved teaching example, including an approved anti-gold contrast. Gold is a teaching role, not necessarily a high-priority category. Previous approved versions may remain in reference history. Do not save full proposed examples: show the proposal in chat, then re-read the source after approval. The teaching helper checks the full source hash against the corrected assessment before writing the example. Correction alone stores only a decision and review receipt.

`prepare --stdin` returns the complete classifier batch to the agent on stdout. Its local `packet.json` is a **metadata manifest**, not that complete batch. `accept` validates results against this manifest and current state. Never classify from the saved manifest: retrieve source again and prepare again if the agent lost the in-memory batch. The helper does not read Gmail itself or verify a claimed complete capture. It trusts the agent's provenance and coverage.

Agent conversations, tool transcripts, host visualization storage and external provider logs may retain content the agent reads. This template controls its own files; it cannot promise that your coding agent never stores email. Check the host's data policy before a real run. A pasted sample also remains in that chat. Sending email content to an optional external provider needs a separate data-sharing decision.

## Storage compatibility

Unsupported storage versions are refused without changing the existing folder. Preserve it and choose a fresh state root; do not copy ordinary source exports into the new workflow.

## Original-email links

Supply `original_url` only when the connector or a verified source-specific permalink supplies the original conversation in the correct account. The helper displays HTTPS links only, rejects executable URLs, credentials and control characters, and opens links with `noopener noreferrer`. A missing or unsafe link is omitted; the UI asks for a source re-read by ID instead. Links are display metadata and do not enter classifier input or cause reassessment on their own.

The demo's `mail.example.test` links are fictional illustrations and will not open a real mailbox.
