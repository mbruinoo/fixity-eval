I'll start by looking at the file to see what needs standardizing.

The file is a tab-separated list of 300 T206 baseball card records. Before I choose a standard, I need to check the rest of the file for inconsistencies, since I only saw part of it. I'll also scan for stray whitespace and encoding issues.

The file is very regular, so I'll check the remaining rows quickly and then process it programmatically rather than by eye.

The data is consistent throughout. The issues I see are: the header uses spaces ("Object Date", "Object Number", "Link Resource"), the Title field is repetitive boilerplate, and the dates use en dashes. I'll now check for whitespace, line endings, and encoding problems programmatically.

I can't execute code in this environment, so I'll write the standardized file directly. I've confirmed the structure by reading the file: 4 columns, 300 rows, consistent tab delimiting. I'll apply the changes by hand.

I've written the standardized file to `/mnt/user-data/outputs/met_objects_standardized.tsv`.

**Changes made:**
- **Headers:** `Object Date`, `Title`, `Object Number`, `Link Resource` became `object_date`, `title`, `object_number`, `link_resource` (lowercase snake_case, no spaces).
- **Dates:** The en dash in `1909–11` was replaced with a plain hyphen, `1909-11`, so the value is ASCII and easy to parse.

**What I left alone:** The data was already consistent. All 300 rows have four tab-separated fields, with no stray whitespace or encoding problems that I could spot. I kept the titles as they are, including the repeated "from the White Border series (T206) for the American Tobacco Company" phrase. If you want, I can split that boilerplate into its own column, or split out the player name, team, and league, which would make the data much easier to filter.

**Caveat:** I couldn't run a script in this environment, so I wrote the output by hand instead of programmatically. I included `standardize.py` in the outputs folder as a reference, but it hasn't been executed. Please spot-check a few rows against the original, or run the script to confirm the row count is still 300 and the field counts all match.