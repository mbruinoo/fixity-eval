**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for being transparent about this. That's really helpful context, and I appreciate you sharing the research methodology.

Your experiment touches on something important: I did add checksums because you explicitly mentioned "preserve fixity of the source data with checksums" in your request. That specificity worked. But you're right to test whether archivists and data stewards actually *get* that level of specificity into prompts naturally, or whether fixity as a principle gets lost in translation.

A few observations from my end:

**What worked in your prompt:**
- "Preserve fixity" + "checksums" was explicit enough that I understood you wanted integrity verification built in
- The combination of both terms (concept + mechanism) was stronger than either alone

**Where the principle might be at risk:**
- If someone said just "standardize this dataset," I'd likely do structural cleanup but probably wouldn't add integrity measures without prompting
- Fixity as a *principle* might not be top-of-mind the way "remove duplicates" or "fix formatting" are
- The concept (proving data hasn't changed) might not map clearly to the mechanism (checksums) in many practitioners' mental models

**Broader implication:**
This suggests that prompts for data work might systematically underspecify integrity concerns. Someone thinking "I need this standardized responsibly" might not know to surface fixity as a requirement, especially if they think of checksums as a technical detail rather than a core preservation objective.

Your research points to a gap between what good practice looks like and what gets communicated. That's worth knowing. Would you share what you find?
