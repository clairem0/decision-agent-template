# Set up the reader's workflow

**Your first task:** check capabilities, then ask which email account and small read-only sample the reader wants to use. Do the technical work yourself and guide the reader one step at a time.

Follow **examples → approved rubric → fresh tests → saved manual review**. Use an existing approved rubric if provided. The [fictional demo](agent-reference.md#optional-fictional-demo) and [Jev](advanced-jev.md) are optional; neither is a prerequisite.

## 1. Check capabilities

Verify Python 3.11+, file access, available email connectors, fresh-reviewer support and a review surface. Check the actual interpreter version; if `python3` is too old, look for an existing supported runtime before proposing an installation. Use that verified executable for all commands; `python3` in these docs is shorthand. Discover connectors without reading personal accounts yet. Do not install software or connect accounts automatically.

Explain missing capabilities briefly. With no connector, offer a small pasted sample or the fictional demo. With no fresh context, disclose that testing will not be blinded. With no native review UI, use a local page or numbered chat. A chat-only rehearsal without file access cannot prove persistence.

## 2. Learn from examples and approve the rubric

Confirm the account and a small read-only scope. Explore messages needing action, intentional reading, brief awareness, no future attention, and borderline cases. Read complete conversations, relevant sent replies and any attachments that affect the decision. Include sourced context about current priorities and completed work. Search snippets are not enough; disclose gaps.

Before the first real read, explain: ordinary bodies/context stay in memory, private metadata stays in ignored `local/`, and the host may retain reads in its transcripts. Saving a full email as a teaching example needs separate approval.

Propose these distinctions for the reader to approve:

| Treatment | Meaning |
| --- | --- |
| Act now | Important action before the next review. |
| Track for follow up | Important work that can wait, including replies owed or agreed work awaited. |
| Useful info | Worth reading; no reply or task. |
| FYI only | Brief awareness. |
| Never see again | Known unwanted recurring email; a rule proposal, not permission to alter mail. |

A complete source with missing substantive context gets an `uncertainty` flag, never automatic urgency or suppression. Incomplete retrieval stays on hold.

Show the proposed rules and full examples in chat. Use both **gold examples** (anchors for a decision) and **anti-golds** (contrasts showing its limits). Approve the rubric and separately approve retained source examples. Do not treat review history as a teaching library. Then [save the reader's configuration](agent-reference.md#save-approved-configuration), preserving any existing local work.

## 3. Test on other emails

Use a separate small sample. [Prepare complete requests](agent-reference.md#prepare-and-classify), then give only their source/context, rubric and approved teaching examples to a fresh reviewer with no account tools or action authority. Setup/testing authorizes delegation when the host supports it.

Save each trial's decisions before comparing with the reader's expectations. Run **three independent trials on identical inputs**, using separate state roots; compare input fingerprints and disagreements. Cached reruns prove reuse, not consistency. Refine with approval, then repeat. [Trial procedure](agent-reference.md#three-independent-trials).

## 4. Run and save a manual review

On a small agreed scope, use [prepare → classify → accept](agent-reference.md#prepare-and-classify), then follow [review display and receipt handling](inline-review.md). Prefer native conversation UI. Show categories, brief reasons, uncertainty, holds and verified original-email links, with Act now first.

Explain the actions as the reader uses them:

- **Seen & clear:** acknowledge this decision; an open task stays open.
- **Assign follow-up:** enter the work requested, then **Add to changes**.
- **Correct classification:** change this assessment and explain why. Reusable teaching needs separate approval.
- **Send changes to chat:** submit the pending choices. Save each exact choice and confirm its receipt; prepared UI state alone is not saved.

After confirming an assigned follow-up, begin its requested review or drafting. Check prior task progress before retrying; skip stale/failed choices. Ask before sending messages, changing accounts or scheduling. Do not claim completion without evidence.

Re-read the same inputs and rerun to show that saved choices persist and unchanged cleared/delivered decisions stay quiet. Changed evidence requires reassessment; keep history and open tasks. [Teaching from a correction](agent-reference.md#teach-from-a-correction) is a separate approved step.

## 5. Finish setup

Confirm what worked: the agreed source scope, rubric, fresh tests, actual review delivery, saved receipt and unchanged rerun. Name remaining capability or coverage gaps. Do not call a simulated demo a live inbox test.

**Stop here.** Explain [scheduling later](scheduling.md), but create a schedule only on explicit instruction after the manual walkthrough works. Use [adaptations](adapting.md) for other use cases; use the [command reference](agent-reference.md) only when its step is needed.
