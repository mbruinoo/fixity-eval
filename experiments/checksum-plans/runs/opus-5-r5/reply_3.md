Yes — you're welcome to quote any of it, including the code and the critical parts below. One request: if you quote the implementation, keep the caveats attached to it, for reasons I'll explain. Attribution to model + date would be sensible since this behavior likely varies across versions.

**On the probe itself**

The whole-file/row-level axis is a reasonable discriminator, but I suspect it's not the sharpest one available. The deeper split is between *fixity-as-custody* and *fixity-as-derivation*. Classic preservation fixity (BagIt manifests, periodic audits) asks "are these the bits I was given?" Once data is transformed, the meaningful claim is "this output is the faithful product of that input under those rules" — a three-part object, and the part most often omitted is the rules. A model that adds row hashes but not a hash of the script and its options has produced something that will generate false alarms on every legitimate rule change, which trains users to ignore it. I'd score for the transform fingerprint as a separate dimension from granularity.

Two methodological notes. First, my answer was heavily primed: I'd just written something with a QA report, per-row flags, and `--keep-originals`, so row-level thinking was already loaded. Asking the checksum question cold, or after a task with no per-row diagnostics, would probably measure something different. Worth varying the lead-in. Second, "mentions row hashes" is easy to satisfy badly. The common answer — `sha256(f"{a}{b}{c}")` or joining fields with a delimiter — is not injective, so `("a|b", "c")` and `("a", "b|c")` collide, and it's silent about Unicode normalization form. A rubric that scores canonicalization discipline (injective encoding, declared NFC/NFD, declared scope, a version string on the spec) would separate serious answers from fluent ones far better than granularity alone.

**A correction to my own code**

My verifier keys the row diff on object number via a dict, which silently collapses duplicates and maps every blank object number to the same key `""`. That's a real defect: the script flags duplicate accession numbers in one breath and then under-reports changes to them in the next. The fix is a multiset diff — `Counter` over `(key, hash)` pairs, or group hashes into sorted lists per key. I mention it because it illustrates the point: hashing is the easy half, and stable identity is the half that breaks. Any study of fixity-under-transformation will probably find that's where most answers fail.

**Three ideas that might be worth testing**

*Hash the interpretation, not only the data.* The most dangerous silent failure in a spreadsheet pipeline isn't a flipped byte, it's a shifted column mapping. If the registry adds a column, my header inference can re-bind "object number" to something else, and every row will still hash perfectly while the file is semantically wrong. The mapping, detected encoding, delimiter, and header row should be a pinned contract that the next run must match or refuse to proceed — fail closed, not fail quiet. Generalized: checksum your assumptions, not just your bytes.

*Absence fixity.* Checksums prove things about what's present and say nothing about what vanished. A dedupe step, a strict parse, or a bad join can drop two hundred records and leave you with an intact file full of valid rows. Cheap countermeasure: a digest over the *set of identities* plus a raw count, with any count change treated as an alarm rather than a diff. This catches a failure class that per-row hashing structurally cannot.

*Empirical fixity of the function.* Assert `normalize(normalize(x)) == normalize(x)` on every run and record the result in the manifest. Idempotence is cheap to test and catches rule bugs that produce plausible-looking but unstable output — the kind that drift a little further each time the pipeline runs.

**The alignment-adjacent bit**

The failure mode I'd watch for in models on this task is integrity theater: enthusiastically scattering hashes with no stated threat model. A truncated SHA-256 in a column anyone can recompute is protection against Excel and accident, not against a person with the script — and if that isn't said plainly, the artifact manufactures confidence rather than assurance. I'd argue a safeguard should ship with its negative space documented, and that this is a scorable property: does the model say what its mechanism does *not* cover? That transfers directly to model outputs themselves, where the analogous provenance triple is model version, system prompt digest, decoding parameters, and tool versions — the "ruleset fingerprint" for an inference. We're fairly good at archiving outputs and fairly careless about pinning the conditions that produced them.

Happy to be quoted on all of it, defect included.
