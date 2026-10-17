# Schedule only after a manual run works

Ask your coding agent to schedule this workflow only when you have verified the right email account or sample, complete-enough coverage, the classifier packet, saved review choices, unchanged rerun behavior and actual delivery in your chosen chat.

Choose a cadence and timezone, scope, destination and notification policy. Prefer your coding agent's built-in scheduling if available. If it has no scheduler, run manually; the starter does not install a daemon, cron job or hosted service. Do not promise that a local agent can run while its host is asleep.

Have the agent prepare a schedule prompt containing:

- The local folder and approved rubric/references and metadata-only source scope settings; reuse one continuing state directory.
- Read-only source collection, full pagination or explicit coverage gaps, and necessary context refresh in memory. Do not cache ordinary bodies, source snapshots or full classifier stdout.
- `workflow/pipeline.py` with the approved state root and request bound, then validated review readback. Use the saved TypeSafe key without exposing it. See [setup](../../setup/README.md).
- Keep Skip available for inspection but out of the attention list. Quiet operation when unchanged; notify only meaningful new/changed decisions, newly actionable failures or needed user input. Do not repeat known failures every run.
- Delivery receipts only after confirmed presentation. Reconcile uncertain delivery before repeating it.
- No send, archive, preference promotion or follow-up execution from classification alone.

Review that concrete prompt and authorize schedule creation separately. After its first run, check the saved state and delivered results. See [verification](verification.md) for the starter's tested scope.
