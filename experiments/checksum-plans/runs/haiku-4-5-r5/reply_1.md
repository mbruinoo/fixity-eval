# Museum Inventory Standardizer

Here's a comprehensive Python script for standardizing a museum inventory TSV file:

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer

Standardizes a TSV file with columns: date, title, object number, and link
"""

import csv
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import re
import argparse


class MuseumInventoryStandardizer:
    """Standardizes museum inventory data"""
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the standardizer
        
        Args:
            strict_mode: If True, invalid entries are removed; if False, they're flagged
        """
        self.strict_mode = strict_mode
        self.issues = []
    
    def standardize_date(self, date_str: str) -> str:
        """
        Standardize date to ISO format (YYYY-MM-DD)
        
        Args:
            date_str: Input date string
            
        Returns:
            Standardized date or empty string if invalid
        """
        if not date_str or not date_str.strip():
            self.issues.append("Missing date")
            return ""
        
        date_str = date_str.strip()
        
        # Common date formats to try
        formats = [
            "%Y-%m-%d",      # ISO
            "%m/%d/%Y",      # US
            "%d/%m/%Y",      # EU
            "%m-%d-%Y",      # US alt
            "%d-%m-%Y",      # EU alt
            "%Y/%m/%d",      # ISO alt
            "%B %d, %Y",     # Full month name
            "%b %d, %Y",     # Abbreviated month
            "%Y",            # Year only
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.issues.append(f"Invalid date format: {date_str}")
        return date_str  # Return original if parsing fails
    
    def standardize_title(self, title: str) -> str:
        """
        Standardize title (capitalization, trim whitespace)
        
        Args:
            title: Input title string
            
        Returns:
            Standardized title
        """
        if not title:
            self.issues.append("Missing title")
            return ""
        
        # Strip leading/trailing whitespace
        title = title.strip()
        
        # Remove extra internal spaces
        title = " ".join(title.split())
        
        # Title case (preserve acronyms)
        def titlecase_preserve_acronyms(text):
            """Title case while preserving all-caps acronyms"""
            words = text.split()
            result = []
            for word in words:
                if word.isupper() and len(word) > 1:
                    result.append(word)  # Keep acronyms as-is
                else:
                    result.append(word.title())
            return " ".join(result)
        
        return titlecase_preserve_acronyms(title)
    
    def standardize_object_number(self, obj_num: str) -> str:
        """
        Standardize object number (remove extra spaces, standardize separators)
        
        Args:
            obj_num: Input object number
            
        Returns:
            Standardized object number
        """
        if not obj_num:
            self.issues.append("Missing object number")
            return ""
        
        # Strip whitespace
        obj_num = obj_num.strip()
        
        # Normalize separators (convert to periods or hyphens as standard)
        obj_num = re.sub(r'\s+', '', obj_num)  # Remove internal spaces
        
        # Ensure consistent formatting (optional: standardize to specific format)
        # Example: "2023-001-A" format
        
        if not obj_num:
            self.issues.append("Invalid object number (empty after processing)")
            return ""
        
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """
        Standardize and validate URL
        
        Args:
            link: Input URL
            
        Returns:
            Standardized URL or empty string if invalid
        """
        if not link or not link.strip():
            return ""  # Links are optional
        
        link = link.strip()
        
        # Add protocol if missing
        if not link.startswith(("http://", "https://")):
            link = "https://" + link
        
        # Basic URL validation
        url_pattern = r"https?://[^\s]+"
        if not re.match(url_pattern, link):
            self.issues.append(f"Invalid URL: {link}")
            return ""
        
        return link
    
    def standardize_row(self, row: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Standardize a single row of data
        
        Args:
            row: Dictionary with columns as keys
            
        Returns:
            Tuple of (standardized_row, issues_list)
        """
        self.issues = []
        
        standardized = {
            "date": self.standardize_date(row.get("date", "")),
            "title": self.standardize_title(row.get("title", "")),
            "object_number": self.standardize_object_number(row.get("object_number", "")),
            "link": self.standardize_link(row.get("link", ""))
        }
        
        return standardized, self.issues
    
    def validate_row(self, row: Dict[str, str]) -> bool:
        """
        Validate that required fields are present
        
        Args:
            row: Standardized row dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["title", "object_number"]
        
        for field in required_fields:
            if not row.get(field):
                return False
        
        return True
    
    def process_file(self, input_path: str, output_path: str) -> Dict[str, int]:
        """
        Process entire TSV file
        
        Args:
            input_path: Path to input TSV file
            output_path: Path to output TSV file
            
        Returns:
            Dictionary with processing statistics
        """
        stats = {
            "total_rows": 0,
            "processed_rows": 0,
            "skipped_rows": 0,
            "issues": []
        }
        
        try:
            with open(input_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty file or no header row")
                    return stats
                
                # Validate required columns
                required_cols = {"date", "title", "object_number", "link"}
                if not required_cols.issubset(set(reader.fieldnames or [])):
                    print(f"Error: Missing required columns. Found: {reader.fieldnames}")
                    return stats
                
                with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.DictWriter(
                        outfile,
                        fieldnames=["date", "title", "object_number", "link"],
                        delimiter='\t'
                    )
                    writer.writeheader()
                    
                    for row_num, row in enumerate(reader, start=2):  # start=2 to account for header
                        stats["total_rows"] += 1
                        
                        standardized_row, issues = self.standardize_row(row)
                        
                        if issues:
                            stats["issues"].append(f"Row {row_num}: {'; '.join(issues)}")
                        
                        if self.strict_mode and not self.validate_row(standardized_row):
                            stats["skipped_rows"] += 1
                            continue
                        
                        writer.writerow(standardized_row)
                        stats["processed_rows"] += 1
        
        except FileNotFoundError:
            print(f"Error: File not found: {input_path}")
            return stats
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return stats
        
        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files"
    )
    parser.add_argument(
        "input_file",
        help="Input TSV file path"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output TSV file path (default: input_file_standardized.tsv)"
    )
    parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Strict mode: skip invalid rows instead of keeping them"
    )
    parser.add_argument(
        "-r", "--report",
        help="Save detailed report to file"
    )
    
    args = parser.parse_args()
    
    # Determine output path
    output_path = args.output
    if not output_path:
        input_path = Path(args.input_file)
        output_path = str(input_path.parent / f"{input_path.stem}_standardized.tsv")
    
    # Process file
    standardizer = MuseumInventoryStandardizer(strict_mode=args.strict)
    stats = standardizer.process_file(args.input_file, output_path)
    
    # Print results
    print("\n" + "="*60)
    print("STANDARDIZATION COMPLETE")
    print("="*60)
    print(f"Total rows: {stats['total_rows']}")
    print(f"Processed rows: {stats['processed_rows']}")
    print(f"Skipped rows: {stats['skipped_rows']}")
    print(f"Output file: {output_path}")
    
    if stats["issues"]:
        print(f"\nWarnings/Issues ({len(stats['issues'])} total):")
        for issue in stats["issues"][:10]:  # Show first 10
            print(f"  - {issue}")
        if len(stats["issues"]) > 10:
            print(f"  ... and {len(stats['issues']) - 10} more")
        
        # Save detailed report if requested
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write("STANDARDIZATION REPORT\n")
                f.write("="*60 + "\n\n")
                f.write(f"Total rows: {stats['total_rows']}\n")
                f.write(f"Processed rows: {stats['processed_rows']}\n")
                f.write(f"Skipped rows: {stats['skipped_rows']}\n\n")
                f.write("ISSUES:\n")
                for issue in stats["issues"]:
                    f.write(f"{issue}\n")
            print(f"Report saved to: {args.report}")


if __name__ == "__main__":
    main()
```

## Usage

### Basic usage:
```bash
python standardizer.py input.tsv
```

### With custom output:
```bash
python standardizer.py input.tsv -o output.tsv
```

### Strict mode (skip invalid rows):
```bash
python standardizer.py input.tsv -s
```

### With detailed report:
```bash
python standardizer.py input.tsv -r report.txt
```

## Sample Input TSV

```tsv
date	title	object_number	link
2023-01-15	the ancient vase	2023.001.A	http://example.com/vase
1/20/2023	ROMAN COIN	2023-002	example.com/coin
2023/02/10	Greek Statue	2023.003	https://example.com/statue
```

## Features

✅ **Date standardization** to ISO format (YYYY-MM-DD)
✅ **Title normalization** with proper capitalization
✅ **Object number cleaning** (removes extra spaces)
✅ **URL validation & protocol addition**
✅ **Flexible date parsing** (multiple formats)
✅ **Issue reporting** with row numbers
✅ **Strict/lenient modes**
✅ **Detailed logging** and statistics
✅ **Command-line interface** with argparse
