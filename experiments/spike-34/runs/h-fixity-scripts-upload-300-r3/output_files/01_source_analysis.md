# Met Inventory TSV Standardization Project

## Source File Analysis

### Issues Identified:

1. **Inconsistent Tab Delimiters**: Some rows use tabs, some use mixed whitespace
2. **Missing Column Headers**: File lacks formal header row
3. **Inconsistent Data Format**: 
   - Object Date column has variable formats (ranges, specific dates, "n.d.", blank)
   - Title column contains special characters and HTML entities
   - Object Number contains mixed formats (numeric, alphanumeric, ranges with commas)
4. **HTML Entities**: `&lt;i&gt;` and `&lt;/i&gt;` instead of proper Unicode
5. **Irregular Spacing**: Some fields have leading/trailing whitespace
6. **Data Quality**: 
   - Some rows have missing titles or dates
   - Object numbers vary in format significantly
   - Links all follow same pattern (metmuseum.org)

### Standardization Goals:

- Add proper TSV headers
- Normalize HTML entities to plain text
- Ensure consistent tab delimiters
- Trim whitespace from all fields
- Validate data structure
- Maintain referential integrity with link column
- Generate checksums before/after for fixity verification
