# Have your AI decide

Teach your AI what needs your attention. Your coding agent reads Gmail, Jev applies your rubric, and you review the results together: **Needs action**, **Worth seeing** or **Skip**. Your inbox stays unchanged.

Leave an item untouched and it stays in the next review. Only a submitted choice clears it from that review; simply showing it does not count as acknowledgment.

## Start here

Open this folder in Claude Code or Codex and paste the prompt below. You'll need Gmail access, Python 3.11+ and a TypeSafe API key; your agent can help check and set these up.

> Help me set up this email decision workflow. Read AGENTS.md and follow setup/README.md. Do the technical work and guide me one step at a time.
>
> Start with my examples and any rubric we've already drafted. Show me the three categories with gold and anti-gold examples so I can approve them.
>
> Help me connect Jev, try a fictional email, then agree with me on a small batch of real messages to send. Show all three categories and save my corrections. Leave my inbox unchanged and stop before scheduling.

## Where to look

- **Review the judgment:** [rubric](rubric/rubric.json) and [gold/anti-gold examples](rubric/examples.json).
- **Set it up with your agent:** [setup instructions](setup/README.md) and [.env.example](.env.example) for your Jev key.
- **See how it runs:** [workflow](workflow/README.md), including the optional in-chat review.

Your agent saves your approved versions in `local/my-review/rubric.json` and `local/my-review/references.json`. Those are the files to revisit when you want to change the judgment.

When you correct a classification, your agent saves it and offers a rubric tweak, a teaching example, or both to improve similar decisions. You review and approve each proposal before it is saved; keeping a full message as an example is a separate choice.
