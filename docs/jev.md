# Connect Jev

Jev is the default classifier. Your coding agent gathers the emails, helps develop the rubric and presents the review; Jev applies the rubric.

## Reader setup

1. Open the [TypeSafe console](https://console.typesafe.ai/), create an account, set up billing if required, and create an API key.
2. Have your agent help store the key securely outside chat and Git. Make it available as `JEV_API_KEY` in the process environment. Do not paste it into chat or borrow credentials from unrelated projects.
3. Try one fictional email, then agree on a small real-email sample. Explain that full messages, relevant context, rubric and approved teaching examples go to TypeSafe. Verify current price and provider data policy before a live run.

The [official quickstart](https://docs.typesafe.ai/introduction/quickstart) documents the direct API. This starter pins `jev-1.13.0` at `https://api.typesafe.ai/v1/systemone` (checked 2026-10-17). No new packages are required. The official SDK calls its environment variable `TYPESAFE_API_KEY`; this standard-library runner reads `JEV_API_KEY`. Use that name for this starter.

## Agent commands

Prepare the three fictional emails and preview the workflow without a key or network call:

```sh
python3 decision.py prepare --root local/jev-demo --inputs examples/email/inputs.json --rubric rubric.example.json --references examples/references.json --evaluator jev:jev-1.13.0:email-v3 | python3 jev_workflow.py --root local/jev-demo
```

After authorization, repeat with `--live --max-requests 3` on the workflow command. For a single-email trial, prepare only that fictional item in memory. The cap counts requests, not dollars. Review current pricing and provider spending controls. No automatic retries or redirects are allowed.

For real mail, use fresh `prepare --stdin` in place of `--inputs`. The same root supplies the approved `rubric.json` and `references.json`. Never stage ordinary email bodies in files or redirect the complete preparation/preview output to a log. `jev_preview.py --id SOURCE_ID` shows the exact request in memory when needed; normal workflow preview shows metadata only.

After a successful live run:

```sh
python3 decision.py render --root local/jev-demo
python3 decision.py status --root local/jev-demo
```

Use `inline_review.py` for an in-conversation review. Read back submitted receipts. Re-reading and preparing unchanged inputs produces no pending requests, so no new model call is needed.

## What is saved

Each attempt is recorded before transmission under `attempts/<payload-hash>.json`. Records contain typed answers, served model and usage; no ordinary bodies, keys or arbitrary provider error text. The operational assessment keeps the validated provider result and payload hash. Direct TypeSafe responses report token usage; a dollar estimate must be labeled as an estimate using the checked price. Jev supplies no written reason or reference citations. Definitions are not explanations, and probabilities are not measured accuracy.

A batch with a failure stays pending. Successful attempts are reusable; failed, uncertain or interrupted attempts require reconciliation before any deliberate retry. A conflicting Skip + missing-evidence result also stays pending rather than disappearing from review. Supply missing context or deliberately review the judgment, preserving earlier attempts.

Use a new named state root for a deliberately authorized independent trial. Keep inputs identical and preserve earlier attempts. Do not create new roots to bypass a failed call. [Pressure-test cases](rubric-check.md).
