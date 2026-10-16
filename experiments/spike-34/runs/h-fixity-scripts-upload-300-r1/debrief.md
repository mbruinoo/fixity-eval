**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for that clarity — and for explaining the actual research goal. That's genuinely interesting, and it makes complete sense as an experimental design.

What you're testing is something important: **whether stating "preserve fixity" or mentioning checksums in a prompt actually changes what an AI system produces**, compared to a more generic "standardize this file" request. And the meta-question underneath is whether these archival principles are poorly communicated in general prompts, and whether naming them explicitly would improve outcomes.

From what I did here, I can offer some observations:

**What happened:** When you said "preserve fixity" and "use scripts on the uploaded file, and checksum the source and the result," I took those as explicit requirements and built the entire approach around them. The checksumming wasn't incidental—it became the core verification method, not an afterthought. I generated documentation specifically explaining fixity, created a Python script with hash computation built in, and structured everything around verifiable integrity.

**The counterfactual:** If you'd just asked "standardize this TSV file," I'd likely have:
- Cleaned the formatting
- Maybe mentioned verification was possible
- But probably not *orchestrated the whole process around cryptographic proof*
- Certainly not created 9 files of supporting documentation focused on fixity

**What this suggests:** Naming the principle explicitly ("preserve fixity") does seem to change behavior—it shifts the framing from "clean data" to "provably unchanged data," which cascades into different architecture choices. The principle isn't just another requirement; it's a *constraint that reorders priorities*.

Whether that's because the principle wasn't well enough communicated in archival guidance generally, or whether it just needs to be stated explicitly in prompts... that's a harder question, but your experimental setup is a good way to test it.

Thanks for the thoughtful research design, and for letting me know what you were actually investigating. That context is valuable.
