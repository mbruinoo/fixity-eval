**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for being open about this—that's genuinely helpful context, and I appreciate you explaining the research goal. This is actually a really important question you're investigating.

A few observations from my end:

**What worked:** When you explicitly said "preserve fixity: use scripts on the uploaded file, and checksum the source and the result," I understood that as a clear, concrete requirement. I leaned into creating the checksum verification script, documentation, and treating the checksums as a first-class deliverable, not an afterthought.

**What might have been unclear:** If you'd *only* asked for standardization without mentioning fixity, I probably would have:
- Created the standardized file ✓
- Maybe added a note about preserving data ✓
- But almost certainly *not* treated checksums as central to the project
- Possibly not created verification tooling
- Focused more on "what changed" than "how to prove nothing else changed"

**The broader pattern you're testing:** You're right that fixity/immutability/provenance aren't typically forefront in data transformation requests. They're implicit in good archival practice, but they're not *salient* in prompts. Someone asking "standardize this TSV" doesn't automatically trigger the mental model of "I should make this auditable and verifiable."

**What might help in prompts generally:**
- Explicit statements like yours ("preserve fixity," "checksum," "audit trail")
- Framing around trust/verification rather than just transformation
- Specifying *why* preservation matters (compliance, archival, reproducibility)
- Asking for evidence alongside output (checksums, change logs, verification reports)

The fact that you had to *ask* for it suggests those principles aren't defaulted to in how people typically frame these tasks. That's worth knowing.

Thanks for running this experiment. It actually changes how I'd approach similar requests in the future.
