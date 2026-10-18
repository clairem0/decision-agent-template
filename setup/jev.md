# Connect Jev

Jev applies your rubric. Your coding agent gathers complete emails, runs the pipeline and presents the review.

**Work emails:** Before sending work emails, make sure your organization has approved Jev/TypeSafe for the email content and context you’ll share, in line with its data privacy policies.

If your workplace approves OpenAI’s API for this data instead, ask your coding agent to adapt the workflow to the [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions). It supports category choices and rubric-based scores. This template includes the Jev integration; an OpenAI integration needs implementation and testing. Confirm approval covers API use and the account’s [data controls](https://developers.openai.com/api/docs/guides/your-data), not just access to ChatGPT.

## Connect your key

1. Open the [TypeSafe console](https://console.typesafe.ai/), create an account and API key, and set up billing if required.
2. Copy [.env.example](../.env.example) to `.env` at the repository root and enter your key locally. The pipeline reads it with `--env-file .env`; you can also supply `JEV_API_KEY` in the process environment. Keep it outside chat and Git.
3. Check current pricing and the provider's data policy with your agent. Full messages, relevant context, your rubric and approved teaching examples go to TypeSafe. Begin with one fictional email, then agree on a small real-email batch.

For a separate live test with no Gmail connection, use the [50-thread synthetic inbox](../workflow/README.md#try-jev-without-gmail). It supplies its own fictional rubric and teaching examples and reports measured timings. The offline four-email demo remains simulated.

## Run the pipeline

Use the [standard pipeline command](README.md#command-for-the-agent). It loads your approved rubric and examples from `local/my-review/`, takes complete messages through stdin, calls Jev and saves the review. It does not fetch Gmail itself. If needed, the [reader-approved temporary-file option](gmail.md#hand-complete-conversations-to-jev) deletes its input before contacting Jev. Removing `--live` gives a metadata-only preview without a key or network call.

Choose `--max-requests` for the agreed batch; it bounds requests, not dollars. An unchanged rerun reuses saved decisions. Follow the [review instructions](../workflow/docs/inline-review.md) to display results and save choices.

To see the interface before connecting anything, use the optional [fictional demo](../workflow/README.md#try-the-fictional-demo). Its saved judgments are simulated; it does not test Jev.

## What is saved

Before each call, the runner records an attempt under the state folder's `attempts/<payload-hash>.json`. It retains typed answers, the served model, usage and the payload hash. Attempt records exclude ordinary email bodies, keys and arbitrary provider error text. See [storage](../workflow/docs/storage.md).

Jev returns categories and an evidence flag, without written reasons or reference citations. Review text labels the category definition; a coding agent's explanation should be identified as its interpretation. Probabilities are not measured accuracy. Dollar estimates must use checked pricing and be labeled as estimates.

## Troubleshooting

Each valid result is saved independently. A failed call leaves that conversation pending while other results remain available. The command prints the partial review and exits with status 2 when calls remain unresolved. Successful attempts can be reused after an interruption; failed, uncertain or interrupted attempts require inspection before any deliberate retry. The runner refuses redirects and does not retry automatically. Preserve the existing attempt records; do not create a new state folder to bypass a failure.

A successful answer with an evidence flag is shown for review, even when Jev recommends Skip. Re-read the source; either add missing context and reassess, or submit Correct classification with the reader’s chosen category and reason (including confirming Skip). The reader’s correction takes effect while the original answer and evidence flag remain in history. Failed retrieval still prevents classification and review choices.

For diagnosing a particular step, the `prepare` command in `workflow/decision.py` builds the complete in-memory batch from fresh stdin, the approved configuration and the Jev evaluator identity in `workflow/jev_workflow.py`. Pass that batch through stdin to `workflow/jev_preview.py --id SOURCE_ID` to inspect a request or `workflow/jev_run.py --id SOURCE_ID` for a single diagnostic call. The latter reads `JEV_API_KEY` from the process environment, needs `--live --max-requests 1` to send, and records an attempt without accepting it into the review. `workflow/jev_workflow.py` validates and accepts a prepared batch; the normal pipeline calls it for you. Do not save diagnostic source or full request output in files or logs; the optional temporary-input exception belongs to `pipeline.py` only.

Use the [rubric check](../workflow/docs/rubric-check.md) for deliberately authorized independent trials. Keep their inputs identical and their state separate from operational reviews.

## API reference

The [official quickstart](https://docs.typesafe.ai/introduction/quickstart) documents the direct API. This starter pins `jev-1.13.0` at `https://api.typesafe.ai/v1/systemone` (checked 2026-10-17) and uses Python's standard library. The official SDK names its key `TYPESAFE_API_KEY`; this starter reads `JEV_API_KEY`.
