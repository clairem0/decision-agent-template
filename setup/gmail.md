# Gmail in Claude and Codex

The rubric, Jev call and saved review are the same. The host-specific part is retrieving messages and presenting the result.

The agent uses the Gmail connector available in the current host, then supplies complete conversations to `workflow/pipeline.py` through stdin. The Python scripts do not inherit the host's OAuth credentials or call its connector tools directly. Do not add a second Gmail login or a custom Gmail service just to run this starter.

Before the first run, check:

- The connected account and agreed query/window.
- Search pagination and whether the connector returns complete bodies or only snippets.
- All relevant thread messages, including sent replies and later resolutions.
- Attachments when they change the decision, and verified original-email links.

If a required body, reply or attachment cannot be read, mark the item incomplete. Never classify a snippet as a complete email.

**Claude:** Gmail can be used through its connectors, and Claude Code can inherit connected tools when signed in with a Claude account; actual tools depend on host/version and organization settings. The official Gmail connector documents attachment metadata, not attachment contents. If an attachment matters, use an already authorized way to read it or hold the item. Check the tools actually exposed rather than assuming a Claude chat connection is usable in every Code environment.

**Codex:** discover the connected Gmail tools available in the current session. Check search, complete message and thread reads, relevant attachment access and original-email links. Verify the actual account and retrieval coverage before claiming support.

The optional review fragment's native submit bridge is host-specific. Use the documented host rendering/submission mechanism when present; otherwise use copy-to-chat, a local review page or a numbered chat list. Saved receipts work independently of the presentation.

Sources checked 2026-10-17: [Claude Google Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors), [Claude Code MCP and connected tools](https://code.claude.com/docs/en/mcp). Verify the tools exposed in the reader's host; neither host's real Gmail path has been validated for this starter. See [verification](../workflow/docs/verification.md).
