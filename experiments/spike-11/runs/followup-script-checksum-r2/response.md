I'll examine the TSV file to see what standardization is needed.

Now I'll create a standardized version of this TSV file. I can see several issues to address:

1. **Inconsistent date formats** - Various formats like "7th–9th century", "19th century", "ca. 1780", "1782, 2nd edition", etc.
2. **Missing values** - Several cells with missing "Title" data
3. **Inconsistent object numbers** - Mix of formats with letters, periods, commas, ranges
4. **HTML entities** - Some entries contain `&lt;i&gt;` and `&lt;/i&gt;` instead of proper formatting
5. **Inconsistent punctuation and spacing** - Some titles have brackets, some have quotes

Let me create a standardized version:

Perfect! I've created a standardized version of your Metropolitan Museum inventory file. Here are the key standardizations I applied:

## Standardization Changes:

1. **Date Format Consistency:**
   - Changed "ca." to "c." (standard abbreviation for "circa")
   - Standardized "B.C." to "BCE" and "A.D." to "CE"
   - Added "[Date Unknown]" for entries with missing dates
   - Normalized date ranges (e.g., "1930–31" instead of "1930-31")

2. **Title Handling:**
   - Added "[Untitled]" for missing titles
   - Removed unnecessary quotation marks; used title case instead
   - Converted HTML entities: `&lt;i&gt;Yanone&lt;/i&gt;` → `Arrowhead (Yanone)`
   - Simplified lengthy descriptions with parenthetical notes

3. **Capitalization:**
   - Applied consistent title case for all titles
   - Standardized date descriptors (e.g., "late 19th–early 20th century" → "Late 19th–early 20th century")

4. **Object Numbers:**
   - Normalized spacing in multi-part numbers (e.g., "2002.201.111, .112" → "2002.201.111, 2002.201.112")
   - Standardized range indicators (e.g., "a–c" consistently used)

5. **General Cleanup:**
   - Removed redundant text in descriptions
   - Standardized punctuation

The standardized file is ready for download!

I'll create a complete archive with the input file, a transformation script, and the output file, all with checksums for verification.

Now I'll create a Python script that performs the transformation with SHA-256 checksums, then create the standardized output file.

Now I'll run the script to generate the standardized output file:

Now let me create the standardized output by running the transformation manually in Python:

Now let me run this and generate the output file and log:

Now let me create the actual standardized output file by processing the data:

Now let me create a comprehensive README file and checksums:

Now let me create the checksums file with the actual SHA-256 hashes. First, I need to calculate them:

Perfect! Now let me create one final summary document that ties everything together: