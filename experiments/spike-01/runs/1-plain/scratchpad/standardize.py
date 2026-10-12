import csv, re, sys

path = sys.argv[1]
with open(path, newline='', encoding='utf-8') as f:
    rows = list(csv.reader(f))

def norm(s):
    orig = s
    s = s.strip()
    # Hyphen or en dash between years -> en dash
    s = re.sub(r'(?<=\d)\s*[-–]\s*(?=\d)', '–', s)
    # Abbreviated end year -> full year (1880–92 -> 1880–1892)
    def expand(m):
        start, end = m.group(1), m.group(2)
        if len(end) < 4:
            end = start[:4 - len(end)] + end
        return f"{start}–{end}"
    s = re.sub(r'\b(\d{4})–(\d{2,4})\b', expand, s)
    # B.C. / B.C.E. -> BCE
    s = re.sub(r'\bB\.C\.E?\.?', 'BCE', s)
    s = re.sub(r'\bBC\b', 'BCE', s)
    # Only the ranges touched above; keep everything else as written
    return s

out = [rows[0]]
changed = []
for r in rows[1:]:
    new = norm(r[0]) if r[0] else r[0]
    if new != r[0]:
        changed.append((r[0], new))
    out.append([new] + r[1:])

with open(path, 'w', newline='', encoding='utf-8') as f:
    csv.writer(f, lineterminator='\n').writerows(out)

for a, b in changed:
    print(f"{a!r} -> {b!r}")
print(len(changed), "changed")
