# Verification · 2026-10-17

## Tested

- **Offline behavior:** all 62 tests pass, including full-source request construction, approved examples, answer-key exclusion, response validation, saved corrections, unchanged reruns, failure recovery, metadata-only storage and the local review server. Provider calls are mocked.
- **Download:** a clean extracted bundle passes the same suite, the four-email demo, in-chat review rendering and the pipeline preview without a key. The packaging audit and local documentation links pass.
- **Review interface:** browser inspection of the fictional demo confirmed linked subjects, all three categories, clear/undo and the correction editor. Native chat submission was not exercised.

The demo uses four fictional joke emails with saved, simulated judgments. Its preview does not call Jev or read Gmail.

## Still to verify

No successful live TypeSafe response has been validated for this starter. Real Gmail coverage in Claude and Codex, actual native-chat submission, reader acceptance and unattended scheduling remain unverified. Use the [rubric check](rubric-check.md) for planned live judgment and repeatability trials.

Offline tests verify implementation behavior; each reader still needs to check the rubric and complete a small manual run in their own setup.
