# Verification · 2026-10-18

## Tested

- **Offline behavior:** all 65 tests pass, including full-source request construction, approved examples, answer-key exclusion, response validation, saved corrections, unchanged reruns, failure recovery, metadata-only storage, summary provenance and the local review server. Regression checks verify that delivery-only items resurface, submitted choices quiet only their own items, retrieval holds recover without acknowledgment, and unchanged Jev results return without another provider call. The socket test was rerun outside the sandbox. Provider calls are mocked.
- **Download:** the 44-file packaging audit passes. The clean extracted bundle walkthrough (suite, four-email demo, in-chat rendering and pipeline preview without a key) and documentation links were last checked October 17.
- **Review interface:** October 18 browser checks passed in light/dark mode at 736px and 320px, plus the sandboxed conversation preview. Verified the single demo label, separate summaries, quieter correction button, visible partial/unchecked coverage, follow-up editing, clear/undo, correction and copy-to-chat handoff. A separate browser check confirmed delivery-only items remain visible, an unsent choice has no saved effect, and only untouched items return after a mixed batch of saved choices; the full local review preserves history and shows the correct awaiting-review count. Native chat submission was not exercised.

The demo uses four fictional examples of everyday inbox situations with saved, simulated judgments. Its preview does not call Jev or read Gmail. The revised examples and styling are ready for reader feedback.

## Still to verify

The correction-to-rubric discussion is wired into agent instructions and both review handoffs; an actual reader approval and fresh-provider evaluation of that loop remain unverified. No successful live TypeSafe response has been validated for this starter. Real Gmail coverage in Claude and Codex, actual native-chat submission, reader acceptance and unattended scheduling remain unverified. Use the [rubric check](rubric-check.md) for planned live judgment and repeatability trials.

Offline tests verify implementation behavior; each reader still needs to check the rubric and complete a small manual run in their own setup.
