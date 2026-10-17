# Use the pattern elsewhere

Keep the same sequence: explore real examples, agree on categories and contrasts, test fresh judgments, then add collection, saved review and scheduling. Change what counts as evidence and a useful decision.

| Use case from the article | Review unit | Examples of decisions and essential context |
| --- | --- | --- |
| Customer support | One complete conversation | Needs attention, waiting, resolved; include replies, ownership and the actual outstanding issue. |
| Applications for human review | One application | Human-review categories or separate dimensions; include relevant submitted evidence and mark missing evidence explicitly. Historical accept/reject outcomes are answer keys, not source evidence. |
| Job postings | One complete posting | Role fit under your approved criteria; distinguish missing requirements from a poor match and keep earlier versions. |
| News about sales accounts | One sourced update | Relevant development versus background; use publication date, original source and the reader's approved account context. |

This folder implements **email**. These are adaptation directions, not bundled connectors or ready-to-run workflows. The email labels, `kind`, UI wording and validation are intentionally small and explicit. Ask your agent to change those together for your use case; changing a JSON label alone is insufficient.

## Paste this prompt

```text
Adapt this decision-agent starter for [use case]. First help me define the decision, the unit of review, the source and what a useful result looks like. Explore a few examples with me, including borderline cases and contrasts. Propose the smallest rubric and context requirements we can test.

Use fictional fixtures while changing the template. Update the source kind, allowed labels, classifier contract, review wording, examples and behavioral tests together. Keep missing evidence distinct from failed retrieval. Preserve source identity, meaningful-input hashes, saved corrections, explicit teaching approval and metadata-only storage. Keep target answer keys out of reviewer input.

Use an existing authorized connector or a sample I supply. Do not add a generic framework or bring in someone else's data. Test Jev on held-out examples and a complete manual review, including correction and unchanged rerun, before discussing a schedule. Keep external actions separately authorized.
```

Start with one source and a small rubric. Keep [Jev](../../setup/jev.md) as the classifier and recheck its judgments against examples from the new task.
