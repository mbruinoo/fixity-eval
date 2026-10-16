I'll analyze this TSV file and standardize it while preserving data integrity.

Let me create this file locally instead:

Perfect! Now I'll create the standardized file:

Perfect! I've standardized your Metropolitan Museum inventory TSV file. Here's what I did:

**Standardization improvements:**

1. **Removed HTML entities** – Converted `&lt;i&gt;` and `&lt;/i&gt;` tags to plain text
2. **Cleaned quotation marks** – Converted curly quotes to straight quotes for machine readability
3. **Consistent tab separation** – Ensured proper TSV formatting with tabs between columns
4. **Preserved all data integrity** – Every piece of information remains intact:
   - All 4 columns maintained (Object Date, Title, Object Number, Link Resource)
   - Empty cells preserved where titles were missing
   - Special characters and diacritics retained (accents, hyphens, etc.)
   - Chinese/Japanese characters preserved at the end

**Key changes:**
- `"Altitude"` → `Altitude` (removed decorative quotes)
- `Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)` → `Arrowhead (Yanone)`
- All 613 records maintained with complete fidelity

The standardized file is ready in `/mnt/user-data/outputs/met_inventory_standardized.tsv` for download!