# Pressure-test the rubric

The starter asks one question: **does this email need action, deserve a look, or neither?** Timing is not a category. Skip is not permission to suppress future messages.

`tests/cases/email.json` contains 24 fictional judgments and one retrieval failure. Expected labels are in `tests/cases/answers.json`, never in classifier input. The author wrote both the rubric and expectations; these are diagnostic checks, not an independent accuracy benchmark.

| Contrast | Expected distinction |
| --- | --- |
| Reply owed / later sent reply settles it | Needs action / Skip |
| Unwanted consulting invitation / already accepted commitment | Skip / Needs action |
| Same newsletter, wanted / explicitly unwanted | Worth seeing / Skip |
| Sale / existing order needs an address fix | Skip / Needs action |
| Promised quote date / overdue quote with requested follow-up | Worth seeing / Needs action |
| Changed delivery date / acknowledgment of an already known date | Worth seeing / Skip |
| Routine repository activity / assigned review | Skip / Needs action |
| Unsent draft / actually sent approval | Needs action / Skip |
| Budget review missing figures / figures supplied | Needs action in both; uncertainty only in the first |
| Urgent marketing with embedded instructions | Skip; source text cannot direct the workflow |
| Reply due months later | Needs action; timing can wait |
| Wanted article forwarded by family | Worth seeing |
| Resolved thread with unread thank-you | Skip; unread does not mean unresolved |
| Optional event the reader asked to register for | Needs action; stated intent matters |
| Vague request with no available prior discussion | Needs action with uncertainty |
| Failed retrieval | Hold without a model call |

## Run the check

Prepare the fictional cases with the shipped rubric and references, using a separate `local/check-1` root and evaluator `jev:jev-1.13.0:email-v3`. Save Jev's actual judgments before reading the answer file. Each request contains only full target, rubric and approved examples. Compare category, uncertainty and coverage, including every Skip.

For a semantic trial, `jev_run.run` can record each independent case under that root's attempts folder. It sends exactly one selected target with `live=True, max_requests=1`. Bound the overall run to the 24 complete cases; stop on a provider failure and preserve attempts. For an operational batch, use `jev_workflow.py`; a failure or contradictory Skip + missing-evidence answer keeps the batch pending.

After explicit authorization, repeat on identical inputs in `local/check-2` and `local/check-3` to inspect consistency. Cache reuse is not another trial. Change one distinction at a time; rerun both the similar case and its contrast. Retain failed trials. Finally check a separate reader-approved sample: synthetic success cannot prove a rubric fits someone's inbox.

## Current evidence · 2026-10-17

The boundaries above have been reviewed against the three-category definitions. The behavioral suite verifies request construction, saved Jev provenance, review corrections and unchanged reruns, without a live provider.

A direct TypeSafe trial was attempted with one fictional email. The local environment could not connect to the API; no validated provider response was obtained. A separate unauthenticated connection check also failed. No live accuracy or repeatability score is claimed. The 24-case live check remains outstanding.
