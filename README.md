# Making decisions with AI

The companion template for [Have Your AI Decide (A Lot of Things)](https://technicallycurious.substack.com/p/have-your-ai-decide-a-lot-of-things) from **Technically Curious**.

Teach your AI what needs your attention. Explore examples together, agree on a rubric, then review your emails as **Needs action**, **Worth seeing** or **Skip**. Start with your regular AI agent; Jev is an optional classifier you can add later. Your inbox stays unchanged unless you explicitly ask for an action.

## Get started

Make your own copy with **Use this template → Create a new repository**, or choose **Code → Download ZIP**. Customize your copy for your own workflow. This repository does not accept contributions.

Open this folder in an AI agent with local file access, such as ChatGPT Work/Codex or Claude Cowork/Code. Your agent checks Python 3.11+ and the available review interface. You can follow the article's prompts one at a time, or paste this:

> Help me set up this email decision workflow. Read AGENTS.md and follow setup/README.md. Briefly explain what's here, then guide me one step at a time and handle the technical work.
>
> Start with my examples and any rubric we've already drafted. Explore what belongs in Needs action, Worth seeing and Skip. Show the proposed rubric as three rows with “Belongs here” and “Goes elsewhere” examples, and get my approval.
>
> Use your own classification to test our rubric on a small agreed sample and show the review UI. Save my submitted choices and help me improve the rubric. If I haven't connected email, offer the bundled synthetic inbox so I can try the workflow without sharing personal data. Leave my inbox unchanged and stop before scheduling or adding Jev unless I've asked for those.

## Start without Jev or an email connection

- **No Jev:** your AI agent applies the rubric and uses the same review interface and saved choices. You don't need a TypeSafe account or API key.
- **No email connection:** ask **“Help me try the workflow with the bundled synthetic emails.”** Your AI agent classifies the [50 fictional conversations](workflow/README.md#try-synthetic-emails-without-a-connector) using their included rubric, then shows the review so you can try choices and corrections. No connector, personal emails or Jev key needed. You can use Jev on the same inbox later if you prefer.
- **Just exploring:** ask **“Can you show me the fictional demo?”** It uses four invented emails and saved, simulated judgments. No email connection or Jev key is needed.

If you'd rather try your own emails without a connector, you can paste a few complete conversations with relevant replies and context. The chat host may retain what you paste. Neither path fetches new mail automatically.

All collected emails appear for review, including **Skip** recommendations. Untouched items return at the next review; only a submitted choice clears or defers them. Filtering future emails requires an explicitly requested rule in your email account.

## Add Jev when you want to try it

Ask **“Help me add Jev to our workflow using our approved rubric.”** Your agent follows [Jev setup](setup/jev.md), helps you store a TypeSafe key locally and tests one fictional email before an agreed real-email batch. Your rubric and review interface stay in place.

To try Jev without any personal data, use the **separate inbox of 50 fully fictional email threads**:

> Help me try Jev on the bundled synthetic inbox. Follow workflow/README.md#try-jev-without-gmail. Use only its fictional emails, rubric and examples; do not connect Gmail or use any personal context. Preview first, then help me run the live test and show the timing breakdown.

The live synthetic test needs your own TypeSafe key. It uses a fictional reader's rubric, separate from your personal workflow, and reports fresh API calls, reused results, timing and agreement with author-written expectations. [See the test flow](workflow/README.md#try-jev-without-gmail).

## Where to look

- **Review the judgment:** [starter rubric](rubric/rubric.json) and [teaching examples](rubric/examples.json).
- **Set it up with your agent:** [setup instructions](setup/README.md).
- **See how it runs:** [workflow](workflow/README.md), including the optional in-chat review.

Your agent saves your approved versions in `local/my-review/rubric.json` and `local/my-review/references.json`. Those are the files to revisit when you want to change the judgment.

When you correct a classification, select **Use to update rubric** to ask your agent to improve the rule for similar decisions. You review and approve each proposal before it is saved; keeping a full message as an example is a separate choice.
