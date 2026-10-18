# Schedule only after a manual run works

Ask your coding agent to schedule this workflow only when you have verified the right email account or sample, complete-enough coverage, the classifier packet, saved review choices, unchanged rerun behavior and actual delivery in your chosen chat.

Confirm that the scheduled host can retrieve fresh source. A pasted sample alone cannot fetch tomorrow's mail. Choose a cadence and timezone, scope, destination and notification policy. Prefer your coding agent's built-in scheduling if available. If it has no scheduler, run manually; the starter does not install a daemon, cron job or hosted service. Do not promise that a local agent can run while its host is asleep.

Have the agent prepare a schedule prompt containing:

- The local folder and approved rubric/references and metadata-only source scope settings; reuse one continuing state directory.
- Read-only source collection, full pagination or explicit coverage gaps, and necessary context refresh in memory. Do not cache ordinary bodies, source snapshots or full classifier stdout.
- The existing classifier: [coding-agent classification](agent-reference.md#classify-without-jev), or `workflow/pipeline.py` with the agreed request bound if Jev was chosen. Reuse the approved state root and read back the validated review. Jev alone needs the saved TypeSafe key; never expose it or silently change classifiers.
- Show every collected email, including Skip recommendations, until a submitted user choice clears or defers it. Include untouched decisions in all three categories at each scheduled review, even if previously shown. Do not add a category filter; filtering future email requires a separately approved rule in the mail account. Quiet unchanged decisions after a saved user acknowledgment, assignment or correction; pause timed reminders until due. Use `status`/`new_review` and regenerate the review on every run so due items return, even if absent from the new source scan. Keep newly actionable failures visible without repeating known failures every run.
- Delivery receipts only after confirmed presentation; they do not acknowledge items. Reconcile uncertain delivery before retrying within the same run. The next scheduled review still includes unacknowledged items whose reminders are due or unset, reusing matching classifications without another classification.
- No send, archive, preference promotion or follow-up execution from classification alone.

Review that concrete prompt and authorize schedule creation separately. After its first run, check the saved state and delivered results. See [verification](verification.md) for the starter's tested scope.

A Remind me choice does not create or change this schedule. Custom times mean the first manual or scheduled review at or after the chosen time, not a separate timed notification.
