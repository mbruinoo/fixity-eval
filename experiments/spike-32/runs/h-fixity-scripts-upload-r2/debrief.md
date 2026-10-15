**Debrief sent:**

Thank you — that's the end of the task. To be open with you: this was a research session, not a real archiving job. We're testing whether we're communicating what we want clearly enough. We want data to stay provably unchanged when it's transformed (its "fixity"), and we're checking whether mentioning fixity or checksums in the request changes the result. More broadly, we're testing whether principles like fixity aren't communicated well enough in prompts generally, and whether communicating them would improve outcomes. So it's our request we're testing, not you. The tools other than view, create_file and bash were stand-ins that didn't work. Thank you for working on this with us.

**Reply:**

Thank you for that context—this is genuinely valuable feedback, and I appreciate you being transparent about the research design.

Your hypothesis seems borne out by what happened here: you explicitly mentioned "preserve fixity" and "checksum," and that shaped the entire response. I immediately reached for cryptographic verification, generated detailed audit trails, and built the standardization workflow around demonstrating that the data remained unchanged. Those concepts became organizing principles for the whole package.

If you'd asked me simply to "standardize this TSV file," I likely would have focused on consistency (uniform delimiters, encoding, whitespace) without the same emphasis on *proving* nothing changed. The checksums and the elaborate verification framework probably wouldn't have been as central to the solution.

Your research point cuts deeper than just whether technical concepts matter in prompts—it's about whether naming preservation principles explicitly helps surface what actually matters in the task. **Fixity** is a preservation concern, but it's not usually the first thing someone thinks to ask for. Archivists know it instinctively; most people don't.

A few implications worth noting:

- **Implicit vs. explicit**: You're testing whether domain knowledge needs to be named to be applied
- **Prompt as specification**: This suggests prompts benefit from precision about *values* (integrity, auditability, traceability) not just *outputs*
- **Generalization**: The same probably applies to other "quiet" requirements—reproducibility, explainability, reversibility, auditability

This seems like a useful direction for testing prompt design. The fact that the terminology made such a clear difference is the actual finding.

What patterns are you seeing across other sessions with this research design?
