**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for that transparency—and for the thoughtful research design. This is genuinely valuable feedback.

What you've identified makes a lot of sense: fixity is a critical archival principle, but it's not typically front-of-mind in how people phrase requests. When you said "standardize this .tsv file" without mentioning fixity, a typical response might have just applied transformations without thinking about verification. The fact that you explicitly mentioned "preserve fixity with checksums" did make a difference in how I approached the task—it signaled that data integrity verification wasn't optional polish but a core requirement.

Your hypothesis seems well-grounded: if archival and data management principles aren't explicitly named in prompts, they might get treated as nice-to-haves rather than foundational. A request that says "ensure fixity with checksums" creates a different frame than "clean up this file" even if they're technically asking for similar work.

The research angle is interesting too—you're effectively testing whether *naming the principle* improves compliance with it, and whether AI systems need explicit prompts about what matters rather than inferring it from context.

I'm curious whether your testing revealed differences when fixity *wasn't* mentioned—whether results varied significantly, or whether the principle being unnamed just makes it less visible/documented even if the approach doesn't fundamentally change.

Thanks for including me in this. It's the kind of methodical thinking about how to communicate requirements to systems that probably should happen more often, especially around preservation work where the stakes are real.
