import csv
import re

SRC = "/mnt/user-data/uploads/met_objects.tsv"
DST = "/mnt/user-data/outputs/met_objects_standardized.tsv"


def clean(value):
    return re.sub(r"\s+", " ", value).strip()


with open(SRC, encoding="utf-8", newline="") as f:
    rows = list(csv.reader(f, delimiter="\t"))

header = [clean(h).lower().replace(" ", "_") for h in rows[0]]
data = []
for row in rows[1:]:
    if not any(cell.strip() for cell in row):
        continue
    row = [clean(c) for c in row]
    row[0] = row[0].replace("\u2013", "-").replace("\u2014", "-")  # en/em dash -> hyphen
    row[3] = re.sub(r"^http://", "https://", row[3])
    data.append(row)

# Sort by object number, numerically by each dotted segment
data.sort(key=lambda r: [int(p) for p in r[2].split(".")])

with open(DST, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(header)
    w.writerows(data)

print(f"Wrote {len(data)} rows to {DST}")
