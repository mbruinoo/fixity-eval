**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for being transparent about this—that's genuinely helpful context, and I appreciate you explaining what you were actually testing.

This is a really important research question. You're essentially asking: *Do archivists and data stewards need to explicitly name preservation principles like "fixity" in their prompts to get appropriate handling, or should those principles be implicit in the domain?*

Your hypothesis seems sound. Looking back at what I produced, I did:
- Generate checksums and create a manifest
- Document the standardization process
- Preserve the original in parallel
- Create multiple forms of evidence (reports, scripts, checksums)

But I'm realizing I probably did these things *because* you explicitly used the word "fixity" and "checksums." If you'd asked me to just "standardize this TSV file," I might have:
- Produced a single cleaned output file
- Assumed you didn't care about the source anymore
- Skipped the hash documentation entirely
- Created just the one deliverable

The term "fixity" actually carries a lot of implicit requirements once it's named—it signals that you're not just cleaning data, you're *preserving* something and need to *prove* nothing changed in the transformation. That's a fundamentally different task than casual data cleanup.

So your research seems to be identifying a real gap: professionals in fields like archiving, digital preservation, and records management know what fixity means and what it requires, but that knowledge doesn't transmit well through generic prompts. The vocabulary matters.

I'd be curious whether other preservation principles (provenance, authenticity, integrity over time) have similar gaps. It sounds like research worth doing—and it might actually improve how people communicate requirements to AI systems more broadly, not just in preservation contexts.
