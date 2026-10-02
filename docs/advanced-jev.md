# Advanced: try Jev

Get the rubric working with your coding agent first. Jev is optional: useful to explore when volume or multiple classification dimensions justify a separate provider.

This folder includes **an offline preview and a working single-request API runner**. The runner saves Jev's typed answers separately; it does not replace your operational coding-agent decisions or generate explanations. No live call runs during setup or tests.

## Ask your agent

```text
Help me try the optional Jev path in docs/advanced-jev.md. Preview one fictional email with its complete rubric and approved teaching examples. Explain the exact content, OpenRouter/TypeSafe destination, current price and data policy.

If I authorize a live experiment, use jev_run.py with --live --max-requests 1 and a key I set locally in the environment. Do not read keys from other projects or ask me to paste a key into chat. Keep ordinary email bodies out of files and request logs. Read back the saved attempt, typed category, uncertainty flag, served model and usage. Compare with my expectation only after saving the result. Do not retry a failed or uncertain paid attempt automatically, change my inbox, or replace my default workflow.
```

## Commands for your agent

Python 3.11+; no packages required. The [official tutorial](https://openrouter.ai/docs/guides/community/jev-tutorial) and [API reference](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request) document `typesafe/jev-1.13` at `https://openrouter.ai/api/alpha/decisions` (checked 2026-10-02). Verify pricing and provider retention before live use. The reader sets `OPENROUTER_API_KEY` in the environment; the helper does not load `.env` files.

Preview one complete fictional request without a key, network call or saved body:

```sh
python3 decision.py prepare --root local/jev-experiment --inputs examples/email/inputs.json --rubric examples/email/rubric.json --references examples/references.json --evaluator jev-experiment:typesafe/jev-1.13:email-v2 | python3 jev_run.py --id mail-demo-a
```

After explicit authorization, use the same preparation with the live flags:

```sh
python3 decision.py prepare --root local/jev-experiment --inputs examples/email/inputs.json --rubric examples/email/rubric.json --references examples/references.json --evaluator jev-experiment:typesafe/jev-1.13:email-v2 | python3 jev_run.py --id mail-demo-a --live --max-requests 1
```

The runner sends exactly one selected target. `--max-requests 1` is a request limit, **not a dollar cap**; agree on the current price and use provider-side spending limits if needed. Do not wrap it in an automatic retry loop. Real email sharing requires a separate decision about its full source, context and approved examples; use fresh `prepare --stdin`, never a saved body file.

The preview contains full source in `state.target`, the rubric and approved teaching examples. Two Choice questions request the email treatment and evidence sufficiency. `jev_preview.py --id mail-demo-a` remains available when only the raw request JSON is needed. Both preview tools consume the complete in-memory batch, not the saved metadata manifest. Do not redirect their stdout to a file.

## Read the result

Live output and `local/jev-experiment/attempts/<payload-hash>.json` include attempt status, input fingerprint, target identity, requested/served model, validated choices, confidence, probabilities and usage when returned. Ordinary source, keys and arbitrary provider text are excluded. Each attempt is written before sending. Repeating the same payload in that attempts folder is blocked, including after failure or interruption.

- `succeeded`: every requested question validated. `requires_review` flags missing substantive evidence; never suppress an uncertain obligation.
- `http_failed`: HTTP error or refused redirect. Inspect the status and provider account before considering a deliberate retry.
- `invalid_response`: incomplete, malformed or unexpected response. No result is accepted.
- `uncertain` or an interrupted `started`: the request may have reached the provider and incurred a charge. Reconcile the outcome first.

A deliberately authorized repeatability trial uses a separate named attempts root, for example `--root local/jev-trial-2/attempts`, while preserving earlier attempts and identical input hashes. Do not use a new root merely to bypass a failure.

Jev returns typed answers, not a generated reason or reference citations. Do not feed its output to `decision.py accept` or relabel it as `coding_agent`/`simulated`. If you later want operational integration, design distinct evaluator provenance and a review path for probabilities/uncertainty, label any separately generated explanation, and validate the whole review/rerun loop first. [Current proof](verification.md).
