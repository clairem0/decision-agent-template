# Run the workflow

Your agent supplies complete Gmail conversations to [pipeline.py](pipeline.py). It sends each email with your approved rubric and teaching examples to Jev, checks the returned classifications and saves the results. Start with the [setup instructions](../setup/README.md#command-for-the-agent).

Run all commands from the repository root with Python 3.11+. Personal state stays in ignored `local/`; ordinary email bodies stay in memory. See [storage](docs/storage.md) for details.

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

## For your agent

[Command reference](docs/agent-reference.md) · [Rubric checks](docs/rubric-check.md) · [Schedule later](docs/scheduling.md)

The scripts, review assets, tests and technical documentation are kept here. To check or package the starter:

```sh
PYTHONPATH=workflow python3 -m unittest discover -s workflow/tests -v
python3 workflow/build_bundle.py
```

The bundle includes only paths listed in [PUBLIC_FILES.txt](PUBLIC_FILES.txt). See the [product contract](docs/spec.md) before changing the implementation and [verification](docs/verification.md) for what has been tested.
