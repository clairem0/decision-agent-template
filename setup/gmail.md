# Gmail in Claude and Codex

The rubric and saved review work with either the coding agent or Jev. The host-specific part is retrieving messages and presenting the result.

The agent uses the Gmail connector available in the current host, then supplies complete conversations to the [chosen classifier](../workflow/docs/agent-reference.md#prepare-and-classify). For Jev, use `workflow/pipeline.py`. For that Jev handoff, use stdin by default or the reader-approved temporary-file option below. The Python scripts do not inherit the host's OAuth credentials or call its connector tools directly. Do not add a second Gmail login or a custom Gmail service just to run this starter.

## Without an email connection

Offer the [bundled synthetic inbox](../workflow/README.md#try-synthetic-emails-without-a-connector) to try fresh classification and review without any connector or personal data. The coding agent can use its fictional rubric and examples without a Jev key; Jev is optional. Skip personal-inbox setup and connector checks on this path. For a quick interface preview, the [fictional demo](../workflow/README.md#try-the-fictional-demo) uses fixed simulated judgments instead.

If the reader prefers their own emails, ask for a few complete conversations pasted into chat, with relevant replies, dates and context. Explain that the chat host may retain what they paste. Use only that supplied sample; do not require Gmail setup or a Jev key.

For a pasted sample, use stable sample IDs such as `sample:batch-1:thread-1`, preserve those IDs on rereads and set coverage to the supplied sample only. Do not invent an account, inbox coverage or original-email URL. Ask about missing replies or attachments; unresolved retrieval gaps stay on hold. Continue the same example discussion, approved rubric and [first review](README.md#3-review-a-first-run). Either classifier can use a complete pasted sample, but Jev requires separate setup and agreement to transmit it. A pasted sample cannot supply new emails to a daily schedule.

## With connected Gmail

Before the first run, check:

- The connected account and agreed query/window.
- Search pagination and whether the connector returns complete bodies or only snippets.
- All relevant thread messages, including sent replies and later resolutions.
- Attachments when they change the decision, and verified original-email links.

If a required body, reply or attachment cannot be read, mark the item incomplete. Never classify a snippet as a complete email.

## Hand complete conversations to Jev

First prove the handoff with one to three approved conversations, before expanding the batch. A fictional API test alone does not check the connector-to-Python handoff.

**Default: memory and stdin.** Normalize the complete reads using the shape in `workflow/demo/inputs.json`. Start the [pipeline command](README.md#command-for-jev) through the host's process tool, send that JSON to process stdin and close input. The command waits for input; it does not fetch Gmail. Keep bodies out of shell arguments, stdout captures and logs.

**Optional: temporary file.** If stdin transfer is awkward in this host, offer this small fallback:

1. Get the reader's explicit approval to write the agreed batch's full emails and context temporarily to disk, then delete the file. Permission to read Gmail or use Jev alone does not cover this. Honor an existing approval within its agreed scope.
2. Create `local/my-review/temporary-input/` and write the same complete normalized JSON as UTF-8 to a fresh filename, such as `batch-001.json`. Use the reader's private, non-synced state folder and owner-only access where available. Do not overwrite an existing file, copy bodies into command arguments or keep a second export.
3. Run the following command with the agreed request bound:

```sh
python3 workflow/pipeline.py --root local/my-review --temporary-input local/my-review/temporary-input/batch-001.json --env-file .env --live --max-requests 3
```

4. Confirm the file is gone. Successful output includes `temporary_input_removed: true`. The pipeline reads and deletes this one file **before** loading the key or calling Jev, including when JSON parsing fails. Removing `--live` previews without a provider call and still consumes the file. If deletion fails, processing stops. A startup error or forced process stop can leave the file behind: check after every run and remove any approved leftover. If the input is needed again, re-read Gmail.

Only a regular `.json` file directly inside the chosen root's `temporary-input/` is accepted; symlinked files or that directory are refused. Refused paths are untouched. This is temporary storage, not secure erasure; it does not change host transcript or backup policies. See [storage](../workflow/docs/storage.md).

## Host checks

**Claude:** Gmail can be used through its connectors, and Claude Code can inherit connected tools when signed in with a Claude account; actual tools depend on host/version and organization settings. The official Gmail connector documents attachment metadata, not attachment contents. If an attachment matters, use an already authorized way to read it or hold the item. Check the tools actually exposed rather than assuming a Claude chat connection is usable in every Code environment.

**Codex:** discover the connected Gmail tools available in the current session. Check search, complete message and thread reads, relevant attachment access and original-email links. Verify the actual account and retrieval coverage before claiming support.

The optional review fragment's native submit bridge is host-specific. Use the documented host rendering/submission mechanism when present; otherwise use copy-to-chat, a local review page or a numbered chat list. Saved receipts work independently of the presentation.

Sources checked 2026-10-17: [Claude Google Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors), [Claude Code MCP and connected tools](https://code.claude.com/docs/en/mcp). Verify the tools exposed in the reader's host; neither host's real Gmail path has been validated for this starter. See [verification](../workflow/docs/verification.md).
