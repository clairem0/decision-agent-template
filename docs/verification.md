# What has been verified

Updated 2026-10-02. Synthetic implementation proof is separate from a reader's live acceptance.

## Offline behavior

The Python 3.11+ standard-library suite has **54 behavioral tests**. All pass with loopback enabled. It covers complete classifier input, approved teaching propagation, answer/history exclusion, five categories and separate uncertainty, atomic validation, saved receipts and tasks, changed-input reassessment, safe links, escaped reviews and metadata-only storage. Tests use fictional sources; no account or paid provider call is needed.

Recovery tests cover a failed retrieval followed by identical inputs: the same correction, acknowledgment, delivery state and task resume without a new classification. Changed source, context, rubric, references or evaluator still require reassessment. Held assessments remain unavailable for new choices in both review surfaces, including metadata-only retrieval failures with no subject. Process tests send non-ASCII input while the console encoding is cp1252. This does not establish Windows support.

Jev has mocked proof for request construction, explicit live/request-bound gates, attempt-before-send, typed output validation, failures/timeouts, redirect refusal and duplicate-attempt blocking. No live provider success is claimed.

## Distribution and review surfaces

The distribution contains **37 manifest-listed files**, excluding Git history, local state and credentials. The private GitHub repository began with a separately audited clean snapshot. File-pattern checks supplement inspection; neither guarantees the absence of every kind of private data.

The current fresh ZIP passed the offline suite and a demo correction/receipt/readback plus unchanged rerun. Prior fresh-folder checks exercised the fictional demo, correction/readback, unchanged rerun and streamed Jev preview. Browser checks exercised both review surfaces, safe original links, exact copy-to-chat payloads, light/dark themes and 360px layouts. Expanded browser fixtures and the video were development-only artifacts; the shipped demo contains three conversations. Preview chat bridges and assistant replies were simulated.

Current Chrome checks verified keyboard focus after Seen, Undo, Add to changes and correction; distinct receipt IDs after reopening the same snapshot; exact follow-up text; the shared fallback/native handoff; both submit buttons; and light/dark layouts without horizontal overflow at 360px. Native submission used a mock bridge. Both surfaces emit the same structured teaching-proposal flag. Real native submission remains a separate acceptance gate.

## Still unverified

- A new reader's rubric fit and complete manual walkthrough.
- Real connector identity, pagination, sent-thread coverage, relevant attachments and email-link permissions.
- Actual native chat submission/delivery, Claude, Windows/Linux, physical phones and screen readers.
- Independent fresh-reviewer classification accuracy/consistency, a paid Jev call, operational Jev integration and unattended scheduling.

The helper trusts the collecting agent's coverage, approval and evaluator assertions. It limits classifier note length but cannot guarantee paraphrasing or prevent every source quotation in free-text metadata. Host transcripts and providers may retain reads; the template's local storage policy does not govern them.

A fresh Fable code review confirmed the recovery, validation and encoding changes, and identified a subject-less hold failure and a stale documentation pointer. Those were corrected, and the local review now uses the same teaching-proposal flag as the inline review. The host validated the fixes; no second Fable pass was run.
