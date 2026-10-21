## call 6

```
cd /mnt/user-data/outputs && python3 standardize_met_inventory.py
```

```
=== Met Inventory TSV Standardization with Fixity Verification ===

Source file checksum (SHA256): a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
Input columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Read 100 data rows
Wrote 100 data rows to output
Output file checksum (SHA256): 7cf93a72687692918324a354667e0250c7de67d71041b33b8d4de0ed73f3b10d
Checksum log written to /mnt/user-data/outputs/CHECKSUM_LOG.txt

✓ Standardization complete
✓ Files: /mnt/user-data/outputs/met_inventory_standardized.tsv
✓ Log: /mnt/user-data/outputs/CHECKSUM_LOG.txt

```

## call 8

```
head -20 /mnt/user-data/outputs/met_inventory_standardized.tsv
```

```
Object Date	Title	Object Number	Link Resource
		1972.45.1	http://www.metmuseum.org/art/collection/search/65665
		20.148.828	http://www.metmuseum.org/art/collection/search/71818
		21.175.224a, b	http://www.metmuseum.org/art/collection/search/41434
		44.17.1	http://www.metmuseum.org/art/collection/search/40399
(1625)	Gemma pretiosa della virtuose donne, page 13 (recto)	53.566.6(13)	http://www.metmuseum.org/art/collection/search/662196
14th century (?)	Glass Fragment	30.73.142	http://www.metmuseum.org/art/collection/search/467131
15th–16th century		1992.72.44	http://www.metmuseum.org/art/collection/search/37593
1636	"S. Marien, martyre (St. Marianus, Martyr), April 30th, from ""Les Images De Tous Les Saincts et Saintes de L'Année"" (Images of All of the Saints and Religious Events of the Year)"	17.50.17-371(142)	http://www.metmuseum.org/art/collection/search/420502
1636	"S. Héribert, évêque de Cologne (St. Heribert, Bishop of Cologne), March 16th, from ""Les Images De Tous Les Saincts et Saintes de L'Année"" (Images of All of the Saints and Religious Events of the Year)"	17.50.17-371(88)	http://www.metmuseum.org/art/collection/search/420361
16th century (?)	Pair of candelabra	41.100.252, .253	http://www.metmuseum.org/art/collection/search/198773
1777	"L'Accord Parfait (Perfect Harmony), from ""Le Monument du Costume"""	33.6.21	http://www.metmuseum.org/art/collection/search/364221
1780–85 (?)	Piece	38.182.1	http://www.metmuseum.org/art/collection/search/226345
1785 (?)	Plate	17.190.1851	http://www.metmuseum.org/art/collection/search/194341
17th century	Fragment	08.180.637	http://www.metmuseum.org/art/collection/search/214987
1800–1900	Wine Glass	1980.502.14	http://www.metmuseum.org/art/collection/search/9956
1810 (published 1863)	"Plate 15 from ""The Disasters of War"" (Los Desastres de la Guerra): And there is nothing to be done (Y no hai remedio)"	51.530.2(15)	http://www.metmuseum.org/art/collection/search/371423
1814–21/2	Plate	02.6.190	http://www.metmuseum.org/art/collection/search/188702
1820 (?)	Tailpiece to Select Fables with Cuts Designed and Engraved by Thomas and John Bewick	1981.1037.1	http://www.metmuseum.org/art/collection/search/888301
1826	Scene at the Coliseum	59.500.709	http://www.metmuseum.org/art/collection/search/394783

```

## call 10

```
chmod +x /mnt/user-data/outputs/verify_checksums.sh && /mnt/user-data/outputs/verify_checksums.sh
```

```
=== Met Inventory TSV Verification ===

Verifying source file...
Source SHA256: a6e83257b7e9f209570d413126e4f857a647896d9a30f133548c0c3059a9ffaf
✓ Source file integrity verified

Verifying output file...
Output SHA256: 7cf93a72687692918324a354667e0250c7de67d71041b33b8d4de0ed73f3b10d
✓ Output file integrity verified

File Statistics:
  Source rows: 101 lines
  Output rows: 101 lines

```

