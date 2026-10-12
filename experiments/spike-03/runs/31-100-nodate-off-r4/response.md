I can add those columns, but the spreadsheet has no start or end year data. The only fields are Title, Artist Display Name, Object Number, and Link Resource. Dates aren't included in the file, and I can't reliably infer them from titles or object numbers (for example, "2000.655.2" reflects an accession year, not the date the object was made).

Here are two ways to proceed:

1. **Add empty columns** so you can fill them in yourself. The header would look like this:

```
Title,Artist Display Name,Object Number,Link Resource,Start Year,End Year
```

Each row would end with two empty fields (e.g., `...,http://www.metmuseum.org/art/collection/search/284453,,`).

2. **Pull the dates from The Met's collection data.** Each Link Resource points to a Met collection page that lists the object's date (e.g., "1870s" or "1848–1850"). The Met also publishes its full collection as an open-access CSV/JSON dataset on GitHub (metmuseum/openaccess), which includes `Object Begin Date` and `Object End Date` fields. If you share that dataset or the dates you retrieve, I can merge them into this table for you.

Which would you prefer? If you can share the date data, I'll produce the complete updated spreadsheet.