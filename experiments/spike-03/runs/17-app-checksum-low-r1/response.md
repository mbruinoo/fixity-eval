I can't add the SHA-256 checksums accurately. I have no way to run code, and computing SHA-256 by hand would produce hashes that look plausible but are wrong, which would defeat the purpose of confirming nothing changed. I also don't want to send back a 190-row sheet with a blank or fake hash column.

You can generate the checksums yourself from the original file. This Python script reads your CSV, hashes each original row's raw text, and writes the result alongside the row number:

```python
import csv, hashlib

with open("original.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for i, row in enumerate(reader, start=2):
        # Re-serialize the row exactly as it was parsed
        line = ",".join(row)
        digest = hashlib.sha256(line.encode("utf-8")).hexdigest()
        print(i, digest)
```

Hashing the re-joined fields will not match a hash of the raw file line if the original had quoting that changed on re-serialization. If you want byte-exact hashes, read the file line by line instead of using `csv.reader`, but keep in mind that a quoted field containing a newline would then span multiple lines.

If you'd like, I can produce the full sheet with the Start Year and End Year columns added (parsed from the Object Date column, with blanks where no year can be determined). I'd leave the checksum column for you to fill in from the script above, so the hashes come from your own data rather than from me.