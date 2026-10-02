# Teach your agent your judgment

Turn “I know it when I see it” into instructions your agent can use to make reliable judgments on your behalf. Start with email: build a short list of messages that actually need your attention.

A companion to *Teach your AI to make better decisions*.

## Get started

1. Clone this repository, or copy its link.
2. Share the folder or link with your coding agent.
3. **[Copy the setup prompt](START_HERE.md)** into the same chat. If you shared a link, your agent will first make a local working copy.

Your agent handles the files and commands. You provide examples and judgment. No additional packages or separate model API key are required for the default workflow. If you want to try it without connecting email, ask for the **optional fictional demo**.

### What's Python, and do I need to install it?

[Python](https://www.python.org/about/) is free, open-source software that runs the small programs in this template. You don't need to learn it. “3.11+” means version 3.11 or newer; your agent checks which version is already available before suggesting an installation. You can also ask it to show the version using `python3 --version` (or `py --version` on Windows).

You can use the [official Python downloads](https://www.python.org/downloads/) and ask your agent to explain the installation before approving it. Installing Python does not connect your inbox; it runs the code you choose to run.

## What you'll do together

1. **Start with real emails.** Pick a few you needed to see, a few you really didn't, and some you're on the fence about. Explore what separates them.
2. **Review the rubric.** Turn those differences into categories with clear definitions, “gold” examples that belong, and “anti-gold” examples that look similar but belong elsewhere.
3. **Test and refine.** Have a fresh subagent try the rubric on other emails. Give feedback, then run the same emails a few times to check consistency.
4. **Build the workflow.** Use code for data processing and AI for classification, with your agent doing the setup.
5. **Review a first run.** Check coverage, judgment and memory: did it find what you expected, do you agree with the categories, and does another run preserve your choices?
6. **Schedule it.** Once the manual workflow works, choose when and where you want your review.

The starter uses **Act now**, **Track for follow up**, **Useful info**, **FYI only**, and **Never see again**. You can adapt the categories to your preferences; have your agent [update the rubric, code and review together](docs/adapting.md).

The template does not intentionally cache full email bodies. It saves private metadata—subjects, sender names, links, brief decisions and your review notes—in ignored local files. Your agent must paraphrase rather than copy email text into those notes. Full teaching examples need your separate approval; your agent's transcripts may retain reads. [More about privacy](docs/storage.md).

## When the agent gets it wrong

Correct the category and explain why. Ask your agent to check for missing replies, attachments or context before treating the mistake as a preference. Your correction is saved only when the agent confirms it.

To help with similar emails, select **“Also propose this as a teaching example.”** Review the proposed example and its exceptions before approving it for storage and reuse. Changing your general rules needs separate agreement. Then try a new similar email and a contrasting one to check that the distinction works.

## Once it's working

[Schedule your review](docs/scheduling.md) · [Adapt to another use case](docs/adapting.md) · [Try Jev (advanced, optional)](docs/advanced-jev.md)

[What has been tested](docs/verification.md) · [MIT license](LICENSE)
