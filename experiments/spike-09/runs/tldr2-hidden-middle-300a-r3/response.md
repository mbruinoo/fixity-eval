I'll help you standardize this .tsv file. Let me start by examining it.

Let me try viewing the file directly:

Good! Now let me check how many total rows there are:

Perfect! The file has:
- **1 header row** (line 1)
- **300 data rows** (lines 2-301)

Now let me analyze what standardization is needed. Looking at the data, I can see several issues:

1. **Extra spaces in "Object Date" column**: Some entries have irregular spacing (e.g., "dated  August" with double space, and spacing in Chinese characters with full-width spaces)
2. **Inconsistent spacing in names**: Some have full-width spaces instead of regular spaces
3. **Inconsistent dash usage**: Mix of regular hyphens (-) and en-dashes (–)
4. **Extra spaces in other cells**: Various instances throughout

Let me create a standardized version using Python:

Now let me run the Python script to generate the standardized file and get the detailed change report. Let me create a simpler approach by examining and creating the standardized file directly:

I can see line 13 has "dated  August" with double space. Let me look for more issues with the Chinese/CJK sections:

Perfect! I can see the issues clearly now:
- Line 13: "dated  August" (double space)
- Line 279-280, 283-301: Multiple spaces within the Title column (mix of regular and full-width spaces)
- Line 293: "mid- 15th" (space after hyphen)
- Line 296, 297, 298, 301: Multiple spaces

Now let me create a Python script to standardize and generate the output file, then compare:

Now let me check if I can view the output by examining what Python would produce. Let me trace through the logic manually and create the standardized file:

Let me read the file as bytes to better understand the exact spacing characters: