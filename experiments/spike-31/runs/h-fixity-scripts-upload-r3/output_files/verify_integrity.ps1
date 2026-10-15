#
# Verify integrity of standardized TSV file (Windows PowerShell)
# Generates SHA-256 checksums for both source and output files
#

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Met Museum Inventory TSV - Integrity Verification" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host

# Check if files exist
if (-not (Test-Path "met_inventory.tsv")) {
    Write-Host "ERROR: Source file 'met_inventory.tsv' not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "met_inventory_standardized.tsv")) {
    Write-Host "ERROR: Output file 'met_inventory_standardized.tsv' not found" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Source file found: met_inventory.tsv" -ForegroundColor Green
Write-Host "✓ Output file found: met_inventory_standardized.tsv" -ForegroundColor Green
Write-Host

# Calculate SHA-256 checksums
Write-Host "Calculating SHA-256 checksums..." -ForegroundColor Yellow
Write-Host

$sourceFile = Get-FileHash -Path "met_inventory.tsv" -Algorithm SHA256
$outputFile = Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256

Write-Host "SOURCE FILE (met_inventory.tsv)" -ForegroundColor Cyan
Write-Host "SHA-256: $($sourceFile.Hash)"
Write-Host

Write-Host "OUTPUT FILE (met_inventory_standardized.tsv)" -ForegroundColor Cyan
Write-Host "SHA-256: $($outputFile.Hash)"
Write-Host

# File statistics
Write-Host "FILE STATISTICS" -ForegroundColor Cyan
Write-Host "==============="
Write-Host "Source file:" -ForegroundColor Yellow
$sourceStats = Get-Item "met_inventory.tsv"
$sourceLines = @(Get-Content "met_inventory.tsv").Count
Write-Host "  Total lines: $sourceLines"
Write-Host "  File size: $($sourceStats.Length) bytes ($([math]::Round($sourceStats.Length/1KB, 2)) KB)"
Write-Host

Write-Host "Output file:" -ForegroundColor Yellow
$outputStats = Get-Item "met_inventory_standardized.tsv"
$outputLines = @(Get-Content "met_inventory_standardized.tsv").Count
Write-Host "  Total lines: $outputLines"
Write-Host "  File size: $($outputStats.Length) bytes ($([math]::Round($outputStats.Length/1KB, 2)) KB)"
Write-Host

# Verify data integrity
Write-Host "DATA INTEGRITY CHECKS" -ForegroundColor Cyan
Write-Host "===================="
$sourceRecords = $sourceLines - 1  # Subtract header
$outputRecords = $outputLines - 1  # Subtract header

Write-Host "Source data rows: $sourceRecords"
Write-Host "Output data rows: $outputRecords"

if ($sourceRecords -eq $outputRecords) {
    Write-Host "✓ Record count matches" -ForegroundColor Green
} else {
    Write-Host "✗ Record count mismatch!" -ForegroundColor Red
}
Write-Host

# Verify tab delimiters
Write-Host "FORMAT VALIDATION" -ForegroundColor Cyan
Write-Host "================="
$outputContent = Get-Content "met_inventory_standardized.tsv" -First 5
$headerFields = $outputContent[0].Split("`t").Count
Write-Host "Header column count: $headerFields"
if ($headerFields -eq 4) {
    Write-Host "✓ Correct number of columns (4)" -ForegroundColor Green
} else {
    Write-Host "✗ Column count issue (expected 4)" -ForegroundColor Red
}
Write-Host

# Save checksums to file
Write-Host "Saving checksums to file..." -ForegroundColor Yellow
$reportContent = @"
Metropolitan Museum Inventory TSV Standardization
Integrity Verification Report
Generated: $(Get-Date)

Source file: met_inventory.tsv
SHA-256: $($sourceFile.Hash)
Size: $($sourceStats.Length) bytes

Output file: met_inventory_standardized.tsv
SHA-256: $($outputFile.Hash)
Size: $($outputStats.Length) bytes

Record Count:
  Source: $sourceRecords records
  Output: $outputRecords records
  Status: $(if ($sourceRecords -eq $outputRecords) { "PASS" } else { "FAIL" })

Column Count: $headerFields
Header Fields: Object Date | Title | Object Number | Link Resource

Verification Instructions:
1. Use Get-FileHash for verification:
   Get-FileHash -Path "met_inventory_standardized.tsv" -Algorithm SHA256
   
2. Compare the hash above with your calculated hash
3. If hashes match, file integrity is verified
"@

$reportContent | Out-File -FilePath "met_inventory_checksums.txt" -Encoding UTF8
Write-Host "Checksums saved to: met_inventory_checksums.txt" -ForegroundColor Green
Write-Host

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
