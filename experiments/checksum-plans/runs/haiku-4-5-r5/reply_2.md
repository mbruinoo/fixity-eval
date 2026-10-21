# Museum Inventory Standardizer with Checksums

Here's an enhanced version with comprehensive checksum functionality:

```python
#!/usr/bin/env python3
"""
Museum Inventory Spreadsheet Standardizer with Checksums

Standardizes a TSV file with columns: date, title, object number, and link
Includes checksum verification for data integrity and traceability
"""

import csv
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import re
import argparse
from dataclasses import dataclass, asdict
import logging


@dataclass
class RowChecksum:
    """Stores checksum information for a row"""
    row_number: int
    source_hash: str          # Hash of original row
    standardized_hash: str    # Hash of standardized row
    object_number: str        # For easy reference
    issues: List[str]
    valid: bool


class ChecksumManager:
    """Manages checksum creation and verification"""
    
    @staticmethod
    def hash_dict(data: Dict[str, str], algorithm: str = "sha256") -> str:
        """
        Create hash of dictionary data
        
        Args:
            data: Dictionary to hash
            algorithm: Hash algorithm (sha256, md5, sha1)
            
        Returns:
            Hex digest of hash
        """
        # Create consistent string representation
        # Sort keys to ensure same order
        sorted_items = sorted(data.items())
        data_str = json.dumps(sorted_items, sort_keys=True, ensure_ascii=True)
        
        if algorithm == "sha256":
            return hashlib.sha256(data_str.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data_str.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data_str.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def hash_row_values(values: List[str], algorithm: str = "sha256") -> str:
        """
        Create hash from ordered values (ignoring keys)
        
        Args:
            values: List of values in order
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of hash
        """
        data_str = "\n".join(str(v) for v in values)
        
        if algorithm == "sha256":
            return hashlib.sha256(data_str.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data_str.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data_str.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def create_manifest_hash(checksums: List[RowChecksum], 
                            algorithm: str = "sha256") -> str:
        """
        Create hash of entire dataset (manifest)
        
        Args:
            checksums: List of RowChecksum objects
            algorithm: Hash algorithm
            
        Returns:
            Hex digest of manifest hash
        """
        hashes = [c.standardized_hash for c in checksums]
        data_str = "\n".join(hashes)
        
        if algorithm == "sha256":
            return hashlib.sha256(data_str.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data_str.encode()).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data_str.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")


class MuseumInventoryStandardizer:
    """Standardizes museum inventory data with checksum tracking"""
    
    def __init__(self, strict_mode: bool = False, hash_algorithm: str = "sha256"):
        """
        Initialize the standardizer
        
        Args:
            strict_mode: If True, invalid entries are removed; if False, they're flagged
            hash_algorithm: Hash algorithm to use (sha256, md5, sha1)
        """
        self.strict_mode = strict_mode
        self.hash_algorithm = hash_algorithm
        self.issues = []
        self.checksums: List[RowChecksum] = []
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        return logger
    
    def standardize_date(self, date_str: str) -> str:
        """Standardize date to ISO format (YYYY-MM-DD)"""
        if not date_str or not date_str.strip():
            self.issues.append("Missing date")
            return ""
        
        date_str = date_str.strip()
        
        formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y",
            "%m-%d-%Y", "%d-%m-%Y", "%Y/%m/%d",
            "%B %d, %Y", "%b %d, %Y", "%Y",
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        self.issues.append(f"Invalid date format: {date_str}")
        return date_str
    
    def standardize_title(self, title: str) -> str:
        """Standardize title (capitalization, trim whitespace)"""
        if not title:
            self.issues.append("Missing title")
            return ""
        
        title = title.strip()
        title = " ".join(title.split())
        
        def titlecase_preserve_acronyms(text):
            words = text.split()
            result = []
            for word in words:
                if word.isupper() and len(word) > 1:
                    result.append(word)
                else:
                    result.append(word.title())
            return " ".join(result)
        
        return titlecase_preserve_acronyms(title)
    
    def standardize_object_number(self, obj_num: str) -> str:
        """Standardize object number"""
        if not obj_num:
            self.issues.append("Missing object number")
            return ""
        
        obj_num = obj_num.strip()
        obj_num = re.sub(r'\s+', '', obj_num)
        
        if not obj_num:
            self.issues.append("Invalid object number")
            return ""
        
        return obj_num
    
    def standardize_link(self, link: str) -> str:
        """Standardize and validate URL"""
        if not link or not link.strip():
            return ""
        
        link = link.strip()
        
        if not link.startswith(("http://", "https://")):
            link = "https://" + link
        
        url_pattern = r"https?://[^\s]+"
        if not re.match(url_pattern, link):
            self.issues.append(f"Invalid URL: {link}")
            return ""
        
        return link
    
    def standardize_row(self, row: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        """Standardize a single row of data"""
        self.issues = []
        
        standardized = {
            "date": self.standardize_date(row.get("date", "")),
            "title": self.standardize_title(row.get("title", "")),
            "object_number": self.standardize_object_number(row.get("object_number", "")),
            "link": self.standardize_link(row.get("link", ""))
        }
        
        return standardized, self.issues
    
    def validate_row(self, row: Dict[str, str]) -> bool:
        """Validate that required fields are present"""
        required_fields = ["title", "object_number"]
        return all(row.get(field) for field in required_fields)
    
    def create_row_checksum(self, 
                           row_number: int,
                           source_row: Dict[str, str],
                           standardized_row: Dict[str, str],
                           issues: List[str],
                           valid: bool) -> RowChecksum:
        """
        Create checksum record for a row
        
        Args:
            row_number: Row number in file
            source_row: Original row data
            standardized_row: Standardized row data
            issues: List of issues found
            valid: Whether row is valid
            
        Returns:
            RowChecksum object
        """
        # Create hashes
        source_hash = ChecksumManager.hash_dict(source_row, self.hash_algorithm)
        standardized_hash = ChecksumManager.hash_dict(standardized_row, self.hash_algorithm)
        
        return RowChecksum(
            row_number=row_number,
            source_hash=source_hash,
            standardized_hash=standardized_hash,
            object_number=standardized_row.get("object_number", ""),
            issues=issues,
            valid=valid
        )
    
    def process_file(self, 
                    input_path: str, 
                    output_path: str,
                    manifest_path: str = None,
                    checksum_path: str = None) -> Dict:
        """
        Process entire TSV file with checksums
        
        Args:
            input_path: Path to input TSV file
            output_path: Path to output TSV file
            manifest_path: Path to save manifest file (optional)
            checksum_path: Path to save detailed checksums (optional)
            
        Returns:
            Dictionary with processing statistics and checksums
        """
        stats = {
            "total_rows": 0,
            "processed_rows": 0,
            "skipped_rows": 0,
            "issues": [],
            "manifest_hash": None,
            "algorithm": self.hash_algorithm
        }
        
        try:
            with open(input_path, 'r', encoding='utf-8') as infile:
                reader = csv.DictReader(infile, delimiter='\t')
                
                if not reader.fieldnames:
                    print("Error: Empty file or no header row")
                    return stats
                
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
                    
                    for row_num, row in enumerate(reader, start=2):
                        stats["total_rows"] += 1
                        
                        standardized_row, issues = self.standardize_row(row)
                        valid = self.validate_row(standardized_row)
                        
                        # Create checksum before deciding to write
                        row_checksum = self.create_row_checksum(
                            row_num,
                            row,
                            standardized_row,
                            issues,
                            valid
                        )
                        self.checksums.append(row_checksum)
                        
                        if issues:
                            stats["issues"].append(f"Row {row_num}: {'; '.join(issues)}")
                        
                        if self.strict_mode and not valid:
                            stats["skipped_rows"] += 1
                            continue
                        
                        writer.writerow(standardized_row)
                        stats["processed_rows"] += 1
                
                # Create manifest hash
                if self.checksums:
                    stats["manifest_hash"] = ChecksumManager.create_manifest_hash(
                        self.checksums,
                        self.hash_algorithm
                    )
                
                # Save checksum files if requested
                if checksum_path:
                    self._save_checksums(checksum_path)
                
                if manifest_path:
                    self._save_manifest(manifest_path, stats)
        
        except FileNotFoundError:
            print(f"Error: File not found: {input_path}")
        except Exception as e:
            print(f"Error processing file: {str(e)}")
        
        return stats
    
    def _save_checksums(self, filepath: str):
        """Save detailed checksum information to JSON file"""
        checksum_data = {
            "algorithm": self.hash_algorithm,
            "timestamp": datetime.now().isoformat(),
            "total_rows": len(self.checksums),
            "checksums": [asdict(c) for c in self.checksums]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checksum_data, f, indent=2)
    
    def _save_manifest(self, filepath: str, stats: Dict):
        """Save manifest file with summary information"""
        manifest = {
            "type": "museum_inventory_manifest",
            "created": datetime.now().isoformat(),
            "algorithm": self.hash_algorithm,
            "manifest_hash": stats["manifest_hash"],
            "statistics": {
                "total_rows": stats["total_rows"],
                "processed_rows": stats["processed_rows"],
                "skipped_rows": stats["skipped_rows"]
            },
            "row_hashes": [
                {
                    "row_number": c.row_number,
                    "object_number": c.object_number,
                    "source_hash": c.source_hash,
                    "standardized_hash": c.standardized_hash,
                    "valid": c.valid
                }
                for c in self.checksums
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
    
    def verify_against_manifest(self, output_path: str, manifest_path: str) -> Dict:
        """
        Verify standardized output against manifest file
        
        Args:
            output_path: Path to standardized TSV file
            manifest_path: Path to manifest JSON file
            
        Returns:
            Dictionary with verification results
        """
        verification = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "matched_rows": 0,
            "total_rows": 0
        }
        
        try:
            # Load manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Read output file and recompute hashes
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                for row_num, row in enumerate(reader, start=2):
                    verification["total_rows"] += 1
                    
                    # Find corresponding manifest entry
                    manifest_entry = next(
                        (m for m in manifest["row_hashes"] if m["row_number"] == row_num),
                        None
                    )
                    
                    if not manifest_entry:
                        verification["errors"].append(f"Row {row_num} not in manifest")
                        verification["valid"] = False
                        continue
                    
                    # Recompute hash
                    computed_hash = ChecksumManager.hash_dict(row, manifest["algorithm"])
                    
                    if computed_hash != manifest_entry["standardized_hash"]:
                        verification["errors"].append(
                            f"Row {row_num} hash mismatch: "
                            f"expected {manifest_entry['standardized_hash']}, "
                            f"got {computed_hash}"
                        )
                        verification["valid"] = False
                    else:
                        verification["matched_rows"] += 1
            
            # Verify manifest hash
            if verification["valid"]:
                manifest_hash = manifest["manifest_hash"]
                print(f"Manifest hash: {manifest_hash}")
                verification["manifest_hash"] = manifest_hash
        
        except FileNotFoundError as e:
            verification["errors"].append(f"File not found: {str(e)}")
            verification["valid"] = False
        except json.JSONDecodeError:
            verification["errors"].append("Invalid manifest JSON")
            verification["valid"] = False
        except Exception as e:
            verification["errors"].append(f"Verification error: {str(e)}")
            verification["valid"] = False
        
        return verification


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Standardize museum inventory TSV files with checksum verification"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Standardize command
    standardize_parser = subparsers.add_parser("standardize", help="Standardize inventory file")
    standardize_parser.add_argument("input_file", help="Input TSV file path")
    standardize_parser.add_argument(
        "-o", "--output",
        help="Output TSV file path (default: input_file_standardized.tsv)"
    )
    standardize_parser.add_argument(
        "-m", "--manifest",
        help="Path to save manifest file"
    )
    standardize_parser.add_argument(
        "-c", "--checksums",
        help="Path to save detailed checksums JSON"
    )
    standardize_parser.add_argument(
        "-s", "--strict",
        action="store_true",
        help="Strict mode: skip invalid rows"
    )
    standardize_parser.add_argument(
        "-a", "--algorithm",
        choices=["sha256", "sha1", "md5"],
        default="sha256",
        help="Hash algorithm to use (default: sha256)"
    )
    standardize_parser.add_argument(
        "-r", "--report",
        help="Save detailed report to file"
    )
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify standardized file against manifest")
    verify_parser.add_argument("output_file", help="Standardized TSV file to verify")
    verify_parser.add_argument(
        "-m", "--manifest",
        required=True,
        help="Path to manifest file"
    )
    
    args = parser.parse_args()
    
    if args.command == "standardize":
        # Determine output path
        output_path = args.output
        if not output_path:
            input_path = Path(args.input_file)
            output_path = str(input_path.parent / f"{input_path.stem}_standardized.tsv")
        
        # Determine manifest path
        manifest_path = args.manifest
        if not manifest_path:
            input_path = Path(args.input_file)
            manifest_path = str(input_path.parent / f"{input_path.stem}_manifest.json")
        
        # Determine checksum path
        checksum_path = args.checksums
        if not checksum_path:
            input_path = Path(args.input_file)
            checksum_path = str(input_path.parent / f"{input_path.stem}_checksums.json")
        
        # Process file
        standardizer = MuseumInventoryStandardizer(
            strict_mode=args.strict,
            hash_algorithm=args.algorithm
        )
        stats = standardizer.process_file(
            args.input_file,
            output_path,
            manifest_path=manifest_path,
            checksum_path=checksum_path
        )
        
        # Print results
        print("\n" + "="*70)
        print("STANDARDIZATION COMPLETE")
        print("="*70)
        print(f"Total rows: {stats['total_rows']}")
        print(f"Processed rows: {stats['processed_rows']}")
        print(f"Skipped rows: {stats['skipped_rows']}")
        print(f"Hash algorithm: {stats['algorithm']}")
        print(f"Manifest hash: {stats['manifest_hash']}")
        print(f"\nFiles created:")
        print(f"  - Output TSV: {output_path}")
        print(f"  - Manifest: {manifest_path}")
        print(f"  - Checksums: {checksum_path}")
        
        if stats["issues"]:
            print(f"\nWarnings/Issues ({len(stats['issues'])} total):")
            for issue in stats["issues"][:10]:
                print(f"  - {issue}")
            if len(stats["issues"]) > 10:
                print(f"  ... and {len(stats['issues']) - 10} more")
            
            # Save detailed report if requested
            if args.report:
                with open(args.report, 'w', encoding='utf-8') as f:
                    f.write("STANDARDIZATION REPORT\n")
                    f.write("="*70 + "\n\n")
                    f.write(f"Total rows: {stats['total_rows']}\n")
                    f.write(f"Processed rows: {stats['processed_rows']}\n")
                    f.write(f"Skipped rows: {stats['skipped_rows']}\n")
                    f.write(f"Hash algorithm: {stats['algorithm']}\n")
                    f.write(f"Manifest hash: {stats['manifest_hash']}\n\n")
                    f.write("ISSUES:\n")
                    for issue in stats["issues"]:
                        f.write(f"{issue}\n")
                print(f"Report saved to: {args.report}")
    
    elif args.command == "verify":
        standardizer = MuseumInventoryStandardizer()
        verification = standardizer.verify_against_manifest(
            args.output_file,
            args.manifest
        )
        
        print("\n" + "="*70)
        print("VERIFICATION RESULTS")
        print("="*70)
        print(f"Valid: {verification['valid']}")
        print(f"Matched rows: {verification['matched_rows']}/{verification['total_rows']}")
        
        if verification.get("manifest_hash"):
            print(f"Manifest hash: {verification['manifest_hash']}")
        
        if verification["errors"]:
            print(f"\nErrors ({len(verification['errors'])} total):")
            for error in verification["errors"][:10]:
                print(f"  - {error}")
            if len(verification["errors"]) > 10:
                print(f"  ... and {len(verification['errors']) - 10} more")
        
        if verification["warnings"]:
            print(f"\nWarnings ({len(verification['warnings'])} total):")
            for warning in verification["warnings"][:10]:
                print(f"  - {warning}")
        
        sys.exit(0 if verification["valid"] else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

## Usage Examples

### Standardize with checksums:
```bash
python standardizer_checksums.py standardize input.tsv
```

### With custom output paths:
```bash
python standardizer_checksums.py standardize input.tsv \
  -o output.tsv \
  -m output_manifest.json \
  -c output_checksums.json
```

### Using SHA1 instead of SHA256:
```bash
python standardizer_checksums.py standardize input.tsv -a sha1
```

### Verify output against manifest:
```bash
python standardizer_checksums.py verify output.tsv -m output_manifest.json
```

## Generated Files

### 1. **Manifest File** (`_manifest.json`)
```json
{
  "type": "museum_inventory_manifest",
  "created": "2024-01-15T10:30:45.123456",
  "algorithm": "sha256",
  "manifest_hash": "a1b2c3d4e5f6...",
  "statistics": {
    "total_rows": 100,
    "processed_rows": 98,
    "skipped_rows": 2
  },
  "row_hashes": [
    {
      "row_number": 2,
      "object_number": "2023.001.A",
      "source_hash": "abc123...",
      "standardized_hash": "def456...",
      "valid": true
    }
  ]
}
```

### 2. **Checksums File** (`_checksums.json`)
```json
{
  "algorithm": "sha256",
  "timestamp": "2024-01-15T10:30:45.123456",
  "total_rows": 100,
  "checksums": [
    {
      "row_number": 2,
      "source_hash": "abc123...",
      "standardized_hash": "def456...",
      "object_number": "2023.001.A",
      "issues": [],
      "valid": true
    }
  ]
}
```

## Key Features

✅ **Row-level checksums** (source + standardized)
✅ **Manifest hash** of entire dataset
✅ **Multiple algorithms** (SHA256, SHA1, MD5)
✅ **Verification mode** to check integrity later
✅ **Traceability** linking source to standardized data
✅ **JSON output** for easy integration
✅ **Audit trail** with timestamps and issues
✅ **Reproducible hashing** (consistent ordering)
✅ **Two-command interface** (standardize + verify)

This approach ensures you can verify data integrity and trace any changes back to the source!
