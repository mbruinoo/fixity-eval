**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for that transparency — that's genuinely valuable context, and I appreciate you explaining what you were actually testing.

Your experiment touches on something real. When you said "preserve fixity with checksums," I treated it as a requirement and built around it, but if you *hadn't* mentioned it explicitly, I likely would have just created the standardized file without the verification infrastructure. The word "fixity" acts as a flag that this is a preservation/archival context where provenance and changeability matter.

What strikes me about your test is that it reveals a gap between what archivists and data professionals *know* matters and what gets naturally communicated in requests. You had to explicitly ask for checksums because the default assumption in "standardize this file" is just... output a cleaner version. The forensic concern — "prove nothing was lost or corrupted in transformation" — doesn't surface unless you name it.

I suspect this is true more broadly: principles that are foundational to a domain (fixity in archival work, reproducibility in research, auditability in compliance) often get skipped in prompts because they're so assumed within the field that people don't realize they're invisible to someone outside it. And if an AI system doesn't have that context baked in, it won't volunteer it.

Your test is essentially asking: *Do you have to spell out every principle you care about, or should they be somehow legible from domain language?* The honest answer is probably "you have to spell them out now," which is a useful thing to know if you're designing requests for systems like this.

I'm curious whether you found differences in the outputs you got across variations of the prompt, or if this was more about baseline testing what happens without explicit fixity language.
