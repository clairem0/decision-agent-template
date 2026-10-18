# Run the workflow

Your agent supplies complete Gmail conversations to [pipeline.py](pipeline.py). It sends each email with your approved rubric and teaching examples to Jev, checks the returned classifications and saves the results. Start with the [setup instructions](../setup/README.md#command-for-the-agent).

Run all commands from the repository root with Python 3.11+. Personal state stays in ignored `local/`; ordinary email bodies stay in memory by default, with an explicitly approved temporary-file handoff available. See [storage](docs/storage.md) for details.

## Review the results

Ask your agent to show all three categories in chat. The [in-chat review interface](docs/inline-review.md) is optional; a numbered list or local review page works too. Jev returns categories, not written reasons. Your coding agent can discuss the original email with you.

Correct a decision and explain why; ask your agent to save the correction. Approve a teaching example separately if you want that distinction used for future emails. This changes the examples sent to Jev, not its model weights.

## Try the fictional demo

Want to see the review before connecting anything? Ask your agent: **“Show me the fictional demo in chat using the included review interface.”** These four fictional emails illustrate situations you might find in your own inbox. Each has an email subject and a separately labeled summary:

| Example of | Subject | Category |
| --- | --- | --- |
| An AI subscription billing issue | Your AI subscription renewal failed | Needs action |
| A tax preparer waiting on your reply | Re: Final forms for your business taxes | Needs action |
| A newsletter you want to read | The best Substack | Worth seeing |
| An unwanted promotion | Another reminder about a clothing sale | Skip |

The complete example conversations and their fictional context are in [demo/inputs.json](demo/inputs.json). The newsletter is invented for this demo, not an actual published issue.

The demo is optional. Its decisions are saved and simulated, so it needs no Gmail access or Jev key. Your agent runs:

```sh
python3 workflow/decision.py demo
```

The local review is written to `local/email-demo/review/index.html`. For an in-chat review, follow the [display instructions](docs/inline-review.md). The examples that teach the rubric live separately in [rubric/examples.json](../rubric/examples.json).

## Try Jev without Gmail

This separate inbox contains **50 distinct fictional conversations**: supplier approvals, billing, reservations, deliveries, repairs, classes, equipment loans, travel, account notices and project work. Some are single messages; others contain sent replies, unsent drafts, resolved requests or conflicting details. Roles, situations and reading preferences were invented from scratch. No personal inbox, user profile, business identity, account IDs or real source links were used. The four-email offline demo above is unchanged.

Your agent handles these steps:

1. **Preview the test.** This reads only the three bundled synthetic input files. No key, Gmail access, expected answers or network calls are needed; nothing is saved.

   ```sh
   python3 workflow/try_jev.py
   ```

2. **Run Jev when requested.** Set up your own key using [Jev setup](../setup/jev.md). This sends all 50 fictional threads, the fictional reader's rubric and the separate teaching examples to TypeSafe. It can make **50 sequential, billable API calls** on a fresh run. The request bound is not a dollar cap. No Gmail connection is used.

   ```sh
   python3 workflow/try_jev.py --live --max-requests 50 --env-file .env
   ```

3. **Review the result and timings.** The command prints the review/report locations and a timing breakdown. Ask your agent to present the review in chat using the reported inline file, following [display instructions](docs/inline-review.md). All unreviewed categories, including Skip, remain visible. For source details, read the matching ID in [synthetic/inbox.json](synthetic/inbox.json); these messages have no real mailbox links. Do not fetch Gmail or add personal context.

The test always uses [its own rubric](synthetic/rubric.json) and [teaching examples](synthetic/examples.json). It never loads `local/my-review/` or the starter's editable personal configuration. Results stay in `local/synthetic-inbox/`; a nonempty unrelated folder is refused. Keep this test fixed. If you want to adapt its rubric, preserve the baseline and deliberately start a separate personalized workflow.

**What the timings mean:** loading samples, preparing requests, classifying/saving, comparing results and building the review are measured separately. API round-trip total and median are included in classification time, and include networking and response decoding. They are not isolated model-inference time. Inbox retrieval is **not used**, not a measured Gmail time of zero. The report gives actual new requests, reused decisions/attempts and token usage for new successful calls. It makes no speed comparison with Gmail or another model.

An unchanged rerun reuses saved results and is labeled accordingly; it does not benchmark fresh Jev speed. Reports and original predictions are kept per run. The [author-written expectations](synthetic/expected.json) are read **only after original Jev predictions have been saved**, never sent to the classifier. Report disagreements, including evidence flags; this small authored set is not a real-inbox accuracy benchmark. Reader corrections do not rewrite those original predictions.

Failures retain their attempts and timing reports. Successful attempts can be reused, but uncertain or failed calls are not automatically resent. Do not change folders or delete attempts to evade that check; inspect the outcome before deliberately repeating a trial. A new independently authorized timing trial may use `--root local/synthetic-trial-2` after the previous run has been reconciled.

## For your agent

[Command reference](docs/agent-reference.md) · [Rubric checks](docs/rubric-check.md) · [Schedule later](docs/scheduling.md)

The scripts, review assets, tests and technical documentation are kept here. To check or package the starter:

```sh
PYTHONPATH=workflow python3 -m unittest discover -s workflow/tests -v
python3 workflow/build_bundle.py
```

The bundle includes only paths listed in [PUBLIC_FILES.txt](PUBLIC_FILES.txt). See the [product contract](docs/spec.md) before changing the implementation and [verification](docs/verification.md) for what has been tested.
