# Museum Inventory Standardizer

```python
#!/usr/bin/env python3
"""
Standardizes museum inventory spreadsheets (.tsv format).
Handles corrections, withdrawals, and duplicate entries.
"""

import csv
import sys
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple


@dataclass
class InventoryEntry:
    """Represents a standardized museum inventory entry."""
    date: str
    title: str
    object_number: str
    link: str
    status: str = "active"  # active, withdrawn, corrected
    notes: str = ""
    
    def is_valid(self) -> bool:
        """Check if entry has required fields."""
        return bool(self.date and self.title and self.object_number)


class MuseumInventoryStandardizer:
    """Standardizes and validates museum inventory data."""
    
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else self.input_file.with_stem(f"{self.input_file.stem}_standardized")
        self.entries: Dict[str, InventoryEntry] = {}
        self.history: List[Dict] = []
        self.errors: List[str] = []
        
    def load_inventory(self) -> None:
        """Load and parse the TSV file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                if not reader.fieldnames:
                    raise ValueError("Empty file or missing header")
                
                required_fields = {'date', 'title', 'object_number', 'link'}
                if not required_fields.issubset(set(reader.fieldnames or [])):
                    raise ValueError(f"Missing required columns. Expected: {required_fields}")
                
                for row_num, row in enumerate(reader, start=2):
                    self._process_row(row, row_num)
                    
        except FileNotFoundError:
            self.errors.append(f"File not found: {self.input_file}")
            raise
        except Exception as e:
            self.errors.append(f"Error loading file: {str(e)}")
            raise
    
    def _process_row(self, row: Dict, row_num: int) -> None:
        """Process and validate a single row."""
        try:
            # Parse action markers (WITHDRAWN, CORRECTED, etc.)
            action, cleaned_row = self._extract_action(row)
            
            # Standardize fields
            date = self._standardize_date(cleaned_row.get('date', '').strip())
            title = cleaned_row.get('title', '').strip()
            object_number = self._standardize_object_number(cleaned_row.get('object_number', '').strip())
            link = self._standardize_link(cleaned_row.get('link', '').strip())
            
            if not object_number:
                self.errors.append(f"Row {row_num}: Missing object number")
                return
            
            entry = InventoryEntry(
                date=date,
                title=title,
                object_number=object_number,
                link=link
            )
            
            # Handle actions
            if action == "WITHDRAWN":
                self._handle_withdrawal(entry, row_num)
            elif action == "CORRECTED":
                self._handle_correction(entry, row_num)
            else:
                self._handle_new_entry(entry, row_num)
                
        except Exception as e:
            self.errors.append(f"Row {row_num}: {str(e)}")
    
    def _extract_action(self, row: Dict) -> Tuple[str, Dict]:
        """Extract action markers from row (WITHDRAWN:, CORRECTED:, etc.)."""
        actions = {"WITHDRAWN", "CORRECTED", "DUPLICATE"}
        action = None
        cleaned_row = row.copy()
        
        # Check title field for action markers
        title = row.get('title', '')
        for act in actions:
            pattern = f"^{act}\\s*:\\s*"
            if re.match(pattern, title, re.IGNORECASE):
                action = act.upper()
                cleaned_row['title'] = re.sub(pattern, '', title, flags=re.IGNORECASE).strip()
                break
        
        return action, cleaned_row
    
    def _standardize_date(self, date_str: str) -> str:
        """Standardize date format to YYYY-MM-DD."""
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        date_formats = [
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.errors.append(f"Could not parse date: {date_str}")
        return date_str
    
    def _standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number format."""
        if not obj_num:
            return ""
        
        # Remove extra whitespace and normalize separators
        obj_num = re.sub(r'\s+', ' ', obj_num).strip()
        
        # Convert common separators to consistent format (periods)
        obj_num = re.sub(r'[\-_/]', '.', obj_num)
        
        # Remove leading zeros in numeric parts (optional - adjust as needed)
        # obj_num = re.sub(r'\.0+(\d)', r'.\1', obj_num)
        
        return obj_num.upper()
    
    def _standardize_link(self, link: str) -> str:
        """Standardize URL format."""
        if not link:
            return ""
        
        link = link.strip()
        
        # Add https if missing
        if link and not link.startswith(('http://', 'https://')):
            link = 'https://' + link
        
        return link
    
    def _handle_new_entry(self, entry: InventoryEntry, row_num: int) -> None:
        """Handle a new or updated entry."""
        if entry.object_number in self.entries:
            # This is an update
            old_entry = self.entries[entry.object_number]
            self.history.append({
                'object_number': entry.object_number,
                'action': 'updated',
                'row': row_num,
                'old_data': asdict(old_entry),
                'new_data': asdict(entry)
            })
        else:
            self.history.append({
                'object_number': entry.object_number,
                'action': 'added',
                'row': row_num
            })
        
        entry.status = "active"
        self.entries[entry.object_number] = entry
    
    def _handle_withdrawal(self, entry: InventoryEntry, row_num: int) -> None:
        """Handle withdrawn entry."""
        if entry.object_number in self.entries:
            old_entry = self.entries[entry.object_number]
            self.history.append({
                'object_number': entry.object_number,
                'action': 'withdrawn',
                'row': row_num,
                'reason': entry.title or "No reason provided"
            })
            old_entry.status = "withdrawn"
            old_entry.notes = f"Withdrawn: {entry.title}"
        else:
            self.errors.append(f"Row {row_num}: Cannot withdraw non-existent object {entry.object_number}")
    
    def _handle_correction(self, entry: InventoryEntry, row_num: int) -> None:
        """Handle corrected entry."""
        if entry.object_number in self.entries:
            old_entry = self.entries[entry.object_number]
            self.history.append({
                'object_number': entry.object_number,
                'action': 'corrected',
                'row': row_num,
                'old_data': asdict(old_entry),
                'new_data': asdict(entry)
            })
            # Update with corrected data
            for field in ['date', 'title', 'link']:
                if getattr(entry, field):
                    setattr(old_entry, field, getattr(entry, field))
            old_entry.notes = f"Corrected on {datetime.now().strftime('%Y-%m-%d')}"
        else:
            self.errors.append(f"Row {row_num}: Cannot correct non-existent object {entry.object_number}")
    
    def get_statistics(self) -> Dict:
        """Generate statistics about the inventory."""
        active = sum(1 for e in self.entries.values() if e.status == "active")
        withdrawn = sum(1 for e in self.entries.values() if e.status == "withdrawn")
        missing_dates = sum(1 for e in self.entries.values() if not e.date)
        missing_links = sum(1 for e in self.entries.values() if not e.link)
        
        return {
            'total_entries': len(self.entries),
            'active_entries': active,
            'withdrawn_entries': withdrawn,
            'missing_dates': missing_dates,
            'missing_links': missing_links,
            'total_errors': len(self.errors)
        }
    
    def save_standardized(self, include_withdrawn: bool = False) -> None:
        """Save standardized inventory to TSV file."""
        entries_to_save = [
            e for e in self.entries.values()
            if include_withdrawn or e.status == "active"
        ]
        
        # Sort by object number
        entries_to_save.sort(key=lambda e: e.object_number)
        
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['date', 'title', 'object_number', 'link', 'status', 'notes']
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
                
                writer.writeheader()
                for entry in entries_to_save:
                    writer.writerow(asdict(entry))
            
            print(f"✓ Standardized inventory saved to: {self.output_file}")
            
        except Exception as e:
            self.errors.append(f"Error saving file: {str(e)}")
            raise
    
    def save_audit_log(self) -> None:
        """Save audit log of all changes."""
        log_file = self.output_file.with_stem(f"{self.output_file.stem}_audit")
        
        try:
            with open(log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'object_number', 'action', 'details'],
                    delimiter='\t'
                )
                writer.writeheader()
                
                for record in self.history:
                    writer.writerow({
                        'timestamp': datetime.now().isoformat(),
                        'object_number': record.get('object_number', ''),
                        'action': record.get('action', ''),
                        'details': str(record)
                    })
            
            print(f"✓ Audit log saved to: {log_file}")
            
        except Exception as e:
            self.errors.append(f"Error saving audit log: {str(e)}")
    
    def save_error_report(self) -> None:
        """Save error report."""
        if not self.errors:
            return
        
        error_file = self.output_file.with_stem(f"{self.output_file.stem}_errors")
        
        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write("Museum Inventory Standardization - Error Report\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Input file: {self.input_file}\n\n")
                f.write(f"Total errors: {len(self.errors)}\n\n")
                
                for error in self.errors:
                    f.write(f"• {error}\n")
            
            print(f"✓ Error report saved to: {error_file}")
            
        except Exception as e:
            print(f"Error saving error report: {str(e)}")
    
    def print_summary(self) -> None:
        """Print summary of standardization."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("MUSEUM INVENTORY STANDARDIZATION SUMMARY")
        print("="*60)
        print(f"Input file:        {self.input_file}")
        print(f"Output file:       {self.output_file}")
        print(f"\nStatistics:")
        print(f"  Total entries:     {stats['total_entries']}")
        print(f"  Active entries:    {stats['active_entries']}")
        print(f"  Withdrawn entries: {stats['withdrawn_entries']}")
        print(f"  Missing dates:     {stats['missing_dates']}")
        print(f"  Missing links:     {stats['missing_links']}")
        print(f"  Errors:            {stats['total_errors']}")
        
        if self.errors:
            print(f"\nFirst 5 errors:")
            for error in self.errors[:5]:
                print(f"  • {error}")
        
        print("="*60 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python script.py <input.tsv> [output.tsv]")
        print("\nExample: python script.py museum_inventory.tsv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        standardizer = MuseumInventoryStandardizer(input_file, output_file)
        standardizer.load_inventory()
        standardizer.save_standardized(include_withdrawn=False)
        standardizer.save_audit_log()
        standardizer.save_error_report()
        standardizer.print_summary()
        
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Example Input File (`museum_inventory.tsv`)

```
date	title	object_number	link
2024-01-15	Ancient Greek Vase	VAS.001	museum.org/vase001
2024-01-16	Roman Coin	COIN.042	museum.org/coin042
2024-01-17	WITHDRAWN: Duplicate entry	VAS.001	
2024-01-18	CORRECTED: Greek Vase (Restored)	VAS.001	museum.org/vase001-v2
2024-01-19	Medieval Manuscript	MS.156	museum.org/ms156
2024-01-20	WITHDRAWN: Loan returned	MS.156	
```

## Usage

```bash
# Basic usage
python museum_standardizer.py museum_inventory.tsv

# Specify output file
python museum_standardizer.py input.tsv output.tsv
```

## Features

- **Date standardization** - Multiple format support
- **Object number normalization** - Consistent formatting
- **URL validation** - Adds https:// if missing
- **Action handling** - Tracks WITHDRAWN and CORRECTED entries
- **Audit logging** - Complete change history
- **Error reporting** - Detailed validation errors
- **Statistics** - Summary of inventory status
- **Duplicate handling** - Identifies and manages duplicates

## Output Files

1. `*_standardized.tsv` - Clean inventory
2. `*_audit.tsv` - Change history
3. `*_errors.txt` - Error report
