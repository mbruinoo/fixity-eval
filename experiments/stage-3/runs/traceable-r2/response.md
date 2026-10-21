I'll standardize this TSV file while maintaining traceability to the original records. Let me create a cleaned version with consistent formatting and a clear structure.

Let me save this to a file you can download:

I'll create the file directly in your outputs folder so you can download it:

Perfect! Now I can create the file for you:

Perfect! I've created a standardized version of your Met inventory file. Here's what I did to improve it:

**Key improvements:**

1. **Added an Original_Row_Number column** at the beginning—this makes each record traceable back to its position in the original file, ensuring you can always verify changes later.

2. **Standardized column headers** to use underscores instead of spaces (Original_Row_Number, Object_Date, Link_Resource) for better compatibility with databases and programming tools.

3. **Filled in missing titles** with [Untitled] where the title field was blank, and [Not specified] where the Object_Date was missing—this makes the data structure more consistent and easier to parse.

4. **Cleaned up quote formatting** in titles to be consistent and properly escaped for TSV format.

5. **Preserved all original data** including special characters, multi-part object numbers, and international text.

The file is ready to download. The Original_Row_Number column means that if you ever need to reference the source record or audit changes, you can easily look up any row by its original position.