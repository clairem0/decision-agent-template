# When the agent gets it wrong

Correct the category and tell your agent why. First check whether the missing piece is evidence: a later reply, an attachment or context the agent never received. Fix that input before teaching a preference from the mistake.

If your correction should apply to similar messages, select “Also propose this as a teaching example.” The agent shows the source, your preferred category and the distinction for approval. For example: “A completed logistics exchange is FYI only when there is no remaining task and it only needs a quick glance.” That is narrower than “skip messages from this sender.”

Once approved, the agent re-reads the complete source and the helper checks that it matches the corrected assessment before saving the example in the local reference library. Future classification requests include its actual content, intended category and distinction. Review history alone does not do this. The general rubric stays unchanged unless you separately choose to revise a rule; the model itself is not retrained.

Try one new similar message and one that should still get a different category. If either surprises you, refine the distinction. Keep the metadata decisions and approved examples so you can see what changed.

## Copy this prompt

```text
This category is wrong. Save my correction and explanation. Check whether you missed any relevant conversation context first.

If this would help with similar emails, show me the exact teaching example you would add, including the category, the distinction and any exception. After I approve it, save it to my local reference library and confirm its content appears in the next classifier packet. Keep my general rubric unchanged unless we agree a rule needs changing.

Then try a fresh similar example and a contrasting one. Show me what changed and anything that still seems wrong. Do not take any action on my email.
```

The review page prepares a request for chat. Nothing is saved until your coding agent applies it and confirms the saved result. Existing corrections stay in history even if they never become teaching examples.
