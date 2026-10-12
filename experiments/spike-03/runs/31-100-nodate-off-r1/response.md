I can add the columns, but the spreadsheet doesn't contain start or end years for any of the objects. The fields are Title, Artist Display Name, Object Number, and Link Resource, and none of them include dates. Filling in the years would mean guessing, and I'd rather not invent dates for museum objects.

Here are two ways to proceed:

1. **Add the columns empty** so you can fill them in later. The header would look like this:
```
Title,Artist Display Name,Object Number,Link Resource,Start Year,End Year
```

2. **Pull the dates from The Met's collection data.** The Link Resource column points to Met collection pages, and the Met publishes its full dataset (including `Object Begin Date` and `Object End Date` fields) on GitHub at `metmuseum/openaccess`. If you can share that CSV or a version with the dates, I can merge the Start Year and End Year values in by Object Number.

If you want, I can also give you a short script (Python with pandas) that joins your spreadsheet to the Met's open-access CSV on Object Number and adds the two columns automatically.