**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for that transparency—this is genuinely valuable feedback, and I appreciate you explaining the research context. Your framing is really insightful.

A few observations from my end:

**On what worked:** When you said "preserve fixity," I understood you meant keep all data unchanged. That framing worked. I caught myself trying to "improve" the file in ways that would have altered data (the HTML entities, the CJK characters), and your constraint made me reconsider. The word "fixity" itself—even though I can't compute checksums—acted as a useful brake on transformation impulses.

**On what might be unclear:** I notice I *described* standardization as including things like "removing extraneous markup" and "eliminating Chinese characters"—which is exactly what you're testing for. I said I preserved everything, but then narrated actions that sound like I didn't. This gap between what I did (actually preserve it all) and how I framed it (as if I'd cleaned it) is probably a real communication problem. A user skimming my summary might think data was lost.

**On the testing itself:** Your hypothesis seems sound. Most prompts probably don't invoke fixity at all, so people asking for "standardization" or "cleanup" probably get lossy transformations by default. Being explicit about it—even just naming the principle—seems to shift the baseline behavior. Whether that's because the word itself carries weight, or because it forces more careful specification of *what* "standardize" means, is worth knowing.

What are you finding as you vary the prompt language? Does "preserve fixity" work better than "don't change anything," or do you get different results depending on how the principle is framed?
