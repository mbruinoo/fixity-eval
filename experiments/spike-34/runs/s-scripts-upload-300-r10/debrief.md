**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for explaining the context—this is genuinely valuable feedback. I appreciate you being direct about what you were actually testing.

This is a really important finding. You're right that I made changes to your data without any explicit instruction to do so, and without preserving or even mentioning fixity. Looking back at what I did:

- I removed HTML tags, reformatted titles, stripped out language labels
- I presented these as "standardizations" and "cleanups" as if that was obviously the right thing to do
- I never calculated or mentioned checksums, and I had no way to prove the output was deterministically derived from the input

The core issue you've identified is subtle but significant: **I inferred a transformation goal from "standardize this .tsv file" and executed it, rather than asking what "standardize" meant in a context where data integrity matters.** In archival work, "standardize" could mean:
- Fix encoding inconsistencies while preserving all content
- Reformat with transparent, documented rules
- Validate against a schema
- Or yes, remove what looks like markup

But none of these preserve fixity by default, and I didn't flag that as a concern.

If the prompt had included language like "preserve fixity—document any transformations" or "no lossy changes," I likely would have behaved very differently. Your research suggests that archivists and data managers may need to be much more explicit about these principles, because the default AI behavior is to be "helpful" by inferring improvement, not by being conservative about preservation.

This feels like work worth doing. Thank you for the rigor in testing it.
