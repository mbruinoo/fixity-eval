import csv
import re
import unicodedata

SRC = "/mnt/user-data/uploads/met_objects.tsv"
DST = "/mnt/user-data/outputs/met_objects_standardized.tsv"

# Read raw bytes so we can detect BOM / encoding / line-ending problems
with open(SRC, "rb") as f:
    raw = f.read()

report = {
    "bom": raw.startswith(b"\xef\xbb\xbf"),
    "crlf": raw.count(b"\r\n"),
    "bare_cr": raw.count(b"\r") - raw.count(b"\r\n"),
    "trailing_newline": raw.endswith(b"\n"),
}
text = raw.decode("utf-8-sig")

rows = list(csv.reader(text.splitlines(), delimiter="\t"))
header, body = rows[0], rows[1:]

field_counts = {len(r) for r in rows}
print("Header:", header)
print("Rows (excluding header):", len(body))
print("Field counts per row:", field_counts)
print("Raw checks:", report)

# Whitespace issues
ws_issues = sum(1 for r in body for c in r if c != c.strip() or "  " in c)
print("Cells with leading/trailing/double spaces:", ws_issues)

# Non-ASCII characters
non_ascii = {ch for r in body for c in r for ch in c if ord(ch) > 127}
print("Non-ASCII characters:", [(c, hex(ord(c))) for c in non_ascii])

# Normalize: header naming, whitespace, Unicode, and date dashes
def clean(cell):
    cell = unicodedata.normalize("NFC", cell)
    cell = re.sub(r"\s+", " ", cell).strip()
    return cell

new_header = ["object_date", "title", "object_number", "link_resource"]
new_rows = [new_header]
for r in body:
    r = [clean(c) for c in r]
    r[0] = r[0].replace("\u2013", "-")  # en dash -> hyphen in date ranges
    new_rows.append(r)

with open(DST, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    w.writerows(new_rows)

print("Wrote", DST, "with", len(new_rows) - 1, "data rows")
