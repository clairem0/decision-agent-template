# Set up Jev with your agent

Give your agent the [setup prompt](START_HERE.md). It should handle these steps with you:

1. **Check Gmail access.** Verify the account and read one complete conversation, including sent replies. Claude and Codex expose different connector tools; the agent adapts those reads to the same pipeline input. See [Gmail setup notes](docs/gmail.md).
2. **Save your rubric.** Start from [rubric.example.json](rubric.example.json) and the [gold/anti-gold examples](examples/references.json). After you approve the definitions, save your versions as `local/my-review/rubric.json` and `local/my-review/references.json`. Those are the files to review and change later.
3. **Connect Jev.** Open the [TypeSafe console](https://console.typesafe.ai/), create an account and API key, and set up billing if required. Copy `.env.example` to `.env` and enter the key locally. Never paste it into chat. The agent checks current price and explains what is sent to TypeSafe.
4. **Try a small batch.** Begin with one fictional message, then agree on real emails to send. The agent supplies complete messages in memory to `pipeline.py`, which uses Jev and saves the results. Keep the inbox unchanged.
5. **Review together.** Ask for the results in chat, including Skip. Save corrections and check an unchanged rerun. The [in-chat review interface](docs/inline-review.md) is an optional convenience; a numbered list works too.

## Command for the agent

Stream the connector's normalized input through stdin; do not save ordinary email bodies to a file:

```sh
python3 pipeline.py --root local/my-review --env-file .env --live --max-requests 5
```

The command expects stdin; it does not fetch Gmail itself. Use the input shape in `examples/email/inputs.json`, adapted to the authorized account. A cap of 5 allows at most five new classifications; choose a cap matching the agreed batch. Without `--live`, it prepares and previews without calling Jev. An unchanged rerun reuses saved decisions.

[Agent guide](docs/agent-guide.md) · [Jev request and recovery details](docs/jev.md) · [Scheduling later](docs/scheduling.md)
