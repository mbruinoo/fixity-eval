#!/usr/bin/env python3
"""
Met Museum Inventory TSV Standardization with Fixity Preservation
Generates checksums before and after standardization to verify data integrity
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksum(data, algorithm='sha256'):
    """Calculate checksum of data (string or bytes)"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()

def calculate_row_checksum(row_dict, algorithm='sha256'):
    """Calculate checksum of a single row"""
    # Create canonical representation: sorted key-value pairs
    canonical = json.dumps(row_dict, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return calculate_checksum(canonical, algorithm)

def calculate_cell_checksum(cell_value, algorithm='sha256'):
    """Calculate checksum of a single cell"""
    if cell_value is None:
        cell_value = ""
    return calculate_checksum(str(cell_value), algorithm)

def standardize_date(date_str):
    """Standardize date field"""
    if not date_str or not date_str.strip():
        return ""
    return date_str.strip()

def standardize_title(title_str):
    """Standardize title field"""
    if not title_str or not title_str.strip():
        return "[Untitled]"
    return title_str.strip()

def standardize_object_number(obj_num):
    """Standardize object number"""
    if not obj_num or not obj_num.strip():
        return ""
    return obj_num.strip()

def standardize_url(url):
    """Standardize URL field"""
    if not url or not url.strip():
        return ""
    url = url.strip()
    # Ensure consistent URL format
    if url and not url.startswith('http'):
        return ""
    return url

def read_and_checksum_source(file_content):
    """Read TSV content and generate source checksums"""
    lines = file_content.split('\n')
    
    source_checksums = {
        'file_full': calculate_checksum(file_content),
        'rows': {}
    }
    
    # Read as CSV to handle quotes properly
    reader = csv.DictReader(
        lines,
        fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'],
        delimiter='\t'
    )
    
    rows = []
    for idx, row in enumerate(reader, 1):
        if row['Object Date'] is None:  # Skip empty rows at end
            break
        rows.append(row)
        
        # Generate checksums for each row and its cells
        row_checksum = calculate_row_checksum(row)
        source_checksums['rows'][idx] = {
            'full_row': row_checksum,
            'cells': {
                'date': calculate_cell_checksum(row.get('Object Date', '')),
                'title': calculate_cell_checksum(row.get('Title', '')),
                'object_number': calculate_cell_checksum(row.get('Object Number', '')),
                'url': calculate_cell_checksum(row.get('Link Resource', ''))
            }
        }
    
    return rows, source_checksums

def standardize_rows(rows):
    """Apply standardization rules to all rows"""
    standardized = []
    
    for row in rows:
        standardized_row = {
            'Object Date': standardize_date(row.get('Object Date', '')),
            'Title': standardize_title(row.get('Title', '')),
            'Object Number': standardize_object_number(row.get('Object Number', '')),
            'Link Resource': standardize_url(row.get('Link Resource', ''))
        }
        standardized.append(standardized_row)
    
    return standardized

def generate_output_checksums(standardized_rows, output_content):
    """Generate checksums for standardized output"""
    output_checksums = {
        'file_full': calculate_checksum(output_content),
        'rows': {}
    }
    
    for idx, row in enumerate(standardized_rows, 1):
        row_checksum = calculate_row_checksum(row)
        output_checksums['rows'][idx] = {
            'full_row': row_checksum,
            'cells': {
                'date': calculate_cell_checksum(row.get('Object Date', '')),
                'title': calculate_cell_checksum(row.get('Title', '')),
                'object_number': calculate_cell_checksum(row.get('Object Number', '')),
                'url': calculate_cell_checksum(row.get('Link Resource', ''))
            }
        }
    
    return output_checksums

def write_tsv(rows, filepath):
    """Write standardized TSV file"""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['Object Date', 'Title', 'Object Number', 'Link Resource'],
            delimiter='\t',
            lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(rows)

def main():
    # Read the original file content from the embedded data
    original_content = """Object Date	Title	Object Number	Link Resource
19th century		91.1.396	http://www.metmuseum.org/art/collection/search/51219
		1972.45.1	http://www.metmuseum.org/art/collection/search/65665
		44.17.1	http://www.metmuseum.org/art/collection/search/40399
4th–3rd century BCE		2002.201.164	http://www.metmuseum.org/art/collection/search/59554
15th–16th century		1992.72.44	http://www.metmuseum.org/art/collection/search/37593
19th century		79.2.447	http://www.metmuseum.org/art/collection/search/47205
19th century		30.75.967	http://www.metmuseum.org/art/collection/search/68930
		21.175.224a, b	http://www.metmuseum.org/art/collection/search/41434
19th century		10.211.836	http://www.metmuseum.org/art/collection/search/60168
		20.148.828	http://www.metmuseum.org/art/collection/search/71818
ca. 1650		36.120.598a, b	http://www.metmuseum.org/art/collection/search/63282
18th–19th century		62.32a, b	http://www.metmuseum.org/art/collection/search/60684
1949, printed ca. 1976	"Lella," Brittany	1976.609.1	http://www.metmuseum.org/art/collection/search/261910
ca. 1927	"Plucky" Lindbergh Ready to "Hop Off" from Lindbergh Exhibit Cards series (W451)	63.350.619.451.6	http://www.metmuseum.org/art/collection/search/765705
1965	11 Pop Artists Portfolio Vol. I	2007.49.427a–k	http://www.metmuseum.org/art/collection/search/375953
probably 17th–18th century	Ancus	36.25.1870	http://www.metmuseum.org/art/collection/search/30846
ca. 1918 (?)	Blouse	C.I.64.69.2	http://www.metmuseum.org/art/collection/search/97854
probably late 17th–early 18th century	Bottle with figure of St. Nicholas (?)	83.1.45	http://www.metmuseum.org/art/collection/search/186259
ca. 4500–4000 B.C. (?)	Bracelet	07.228.65a	http://www.metmuseum.org/art/collection/search/570998
ca. 1525–30 (?)	Bust of a gentleman in contemporary dress	41.190.479	http://www.metmuseum.org/art/collection/search/199000
ca. 1575	Bust of a man	30.135.7	http://www.metmuseum.org/art/collection/search/196690
probably 18th century	Carpet Fragment	57.150.4	http://www.metmuseum.org/art/collection/search/451459
December 14, 1857	Comment,...c'est-t'y Dieu possible!..., from Actualités, published in Le Charivari, December 14, 1857	22.61.238	http://www.metmuseum.org/art/collection/search/678715
probably 1878	Côte des Grouettes, near Pontoise	1991.277.2	http://www.metmuseum.org/art/collection/search/437316
1875–79	Design for Elevation of Ceiling and Wall, Deepdene, Dorking, Surrey	67.827.9	http://www.metmuseum.org/art/collection/search/345574
n.d.	Design from the Workshop of Froment-Meurice	56.500.154	http://www.metmuseum.org/art/collection/search/384694
1896	Elles (poster for 1896 exhibition at La Plume)	58.621.16	http://www.metmuseum.org/art/collection/search/334196
spring/summer 1985	Ensemble	1998.508.44a–c	http://www.metmuseum.org/art/collection/search/81435
mid-20th century	Esu Figures	1974.388.1	http://www.metmuseum.org/art/collection/search/309993
early 16th century (?)	Fragment	2002.494.130	http://www.metmuseum.org/art/collection/search/230152
probably 15th century	Fragment	08.256.360	http://www.metmuseum.org/art/collection/search/445628
17th century	Fragment	08.180.637	http://www.metmuseum.org/art/collection/search/214987
19th century (?)	Galloon	36.90.1914	http://www.metmuseum.org/art/collection/search/224995
19th century (?)	Galloon	36.90.1951	http://www.metmuseum.org/art/collection/search/225032
(1625)	Gemma pretiosa della virtuose donne, page 13 (recto)	53.566.6(13)	http://www.metmuseum.org/art/collection/search/662196
1921	Georges Carpentier from Boxers Exhibits series (W467)	63.350.618.467.138	http://www.metmuseum.org/art/collection/search/761831
14th century (?)	Glass Fragment	30.73.142	http://www.metmuseum.org/art/collection/search/467131
19th century (?)	Handbell	89.4.1867	http://www.metmuseum.org/art/collection/search/502466
1935–43	Hudson Street	43.33.676	http://www.metmuseum.org/art/collection/search/374634
ca. 1885	Jas. Madison from Presidents (N346), issued by Thomas H. Hall Tobacco to promote Between the Acts and Bravo Cigarettes	Burdick 223, N346.4	http://www.metmuseum.org/art/collection/search/893466
1935–43	Jockey Room	43.33.243	http://www.metmuseum.org/art/collection/search/398263
1777	"L'Accord Parfait (Perfect Harmony), from ""Le Monument du Costume"""	33.6.21	http://www.metmuseum.org/art/collection/search/364221
November 7, 1844	L'Ouverture de la Chasse, from Les Beaux Jours de la Vie, publlished in Le Charivari, November 7, 1844	49.74.25	http://www.metmuseum.org/art/collection/search/641376
20th–mid 20th century	Landscape with canal	69.623.7	http://www.metmuseum.org/art/collection/search/428806
early 19th century, crystal bust possibly 17th or 18th century	Laudomia de' Medici	32.75.72	http://www.metmuseum.org/art/collection/search/197003
ca. 1920–30	Leo Fisher from Movie Stars Exhibit Cards series (W401)	63.350.614.401.193	http://www.metmuseum.org/art/collection/search/774745
1900s–1930s	Main Street, looking West, Elkin, North Carolina	1994.264.107.643	http://www.metmuseum.org/art/collection/search/289842
19th century (?)	Mary, Queen of Scots	58.549.427	http://www.metmuseum.org/art/collection/search/642874
1870	May God Bless That Little Church Around the Corner (Sheet Music cover)	54.90.829	http://www.metmuseum.org/art/collection/search/380894
1890	Miss Foujere, from the Actresses series (N245) issued by Kinney Brothers to promote Sweet Caporal Cigarettes	63.350.219.245.725	http://www.metmuseum.org/art/collection/search/653876
1888	Officer, 4th Regiment, Iowa, National Guard, from the Military Series (N224) issued by Kinney Tobacco Company to promote Sweet Caporal Cigarettes	Burdick 218, N224.92	http://www.metmuseum.org/art/collection/search/722871
16th century (?)	Pair of candelabra	41.100.252, .253	http://www.metmuseum.org/art/collection/search/198773
1780–85 (?)	Piece	38.182.1	http://www.metmuseum.org/art/collection/search/226345
1785 (?)	Plate	17.190.1851	http://www.metmuseum.org/art/collection/search/194341
1814–21/2	Plate	02.6.190	http://www.metmuseum.org/art/collection/search/188702
1810 (published 1863)	Plate 15 from "The Disasters of War" (Los Desastres de la Guerra): And there is nothing to be done (Y no hai remedio)	51.530.2(15)	http://www.metmuseum.org/art/collection/search/371423
ca. 1750–70	River Scene with Castle	53.600.237	http://www.metmuseum.org/art/collection/search/773159
probably 19th–20th century	Rooster	58.156	http://www.metmuseum.org/art/collection/search/202249
Probably 19th century	Rowel Spur (Left), in the Style of the 15th Century	42.50.289	http://www.metmuseum.org/art/collection/search/29218
1636	S. Héribert, évêque de Cologne (St. Heribert, Bishop of Cologne), March 16th, from "Les Images De Tous Les Saincts et Saintes de L'Année" (Images of All of the Saints and Religious Events of the Year)	17.50.17-371(88)	http://www.metmuseum.org/art/collection/search/420361
1636	S. Marien, martyre (St. Marianus, Martyr), April 30th, from "Les Images De Tous Les Saincts et Saintes de L'Année" (Images of All of the Saints and Religious Events of the Year)	17.50.17-371(142)	http://www.metmuseum.org/art/collection/search/420502
1826	Scene at the Coliseum	59.500.709	http://www.metmuseum.org/art/collection/search/394783
ca. 1929–30	Sultan Miramolin with his minsters and warriors, illustration for page 7 of  "The Book of Christopher Columbus: a Lyrical Drama in Two Parts" (New Haven and London 1930)	30.33(13)	http://www.metmuseum.org/art/collection/search/734927
ca. 1875–1900	Sword with Scabbard	36.25.1553a, b	http://www.metmuseum.org/art/collection/search/31004
1820 (?)	Tailpiece to Select Fables with Cuts Designed and Engraved by Thomas and John Bewick	1981.1037.1	http://www.metmuseum.org/art/collection/search/888301
ca. 1545–50 (?)	The Adoration of the Magi	27.78.2(57)	http://www.metmuseum.org/art/collection/search/366253
ca. 1852-1863	The London Omnibus	2022.457.4a–d	http://www.metmuseum.org/art/collection/search/893945
August 26, 1873	The Wreck of the "Atlantic" – Cast Up by the Sea (from "Harper's Weekly," Vol. XVII)	29.88.9(1)	http://www.metmuseum.org/art/collection/search/392210
ca. 2030–1640 B.C.	Toilet Jar	31.3.82	http://www.metmuseum.org/art/collection/search/561896
ca. 1938	Untitled (female figures)	1979.292.707	http://www.metmuseum.org/art/collection/search/497016
1800–1900	Wine Glass	1980.502.14	http://www.metmuseum.org/art/collection/search/9956
18th century (?)	Woman's Mantle	1999.47.255	http://www.metmuseum.org/art/collection/search/318175
May 1947	[45 Contact Sheets with Miscellaneous Negative Sleeves, Contact Prints, and Storage Envelopes Relating to "One Newspaper Town", Published in Fortune Magazine August 1947]	1994.250.18	http://www.metmuseum.org/art/collection/search/281799
1860s	[Andrew McCallum]	1970.659.559	http://www.metmuseum.org/art/collection/search/685899
1929–34	[Baby]	1994.256.458	http://www.metmuseum.org/art/collection/search/275137
July–August 1933	[Detail of "Shays' Rebellion" Panel of Diego Rivera's Mural for the New Worker's School, New York City]	1994.256.301	http://www.metmuseum.org/art/collection/search/274965
1860s	[Egron Sellif Lundgren]	1970.659.538	http://www.metmuseum.org/art/collection/search/685878
1900s–1930s	[Paper Moon Studio Portrait]	2018.369.248	http://www.metmuseum.org/art/collection/search/775136
1860s	[Sanford Robinson Gifford]	1970.659.343	http://www.metmuseum.org/art/collection/search/685683
March 1935	[Thirty-One 35mm Film Frames on Uncut Roll: Louisiana]	1994.253.443 (1–31)	http://www.metmuseum.org/art/collection/search/717070
1933 (?)	[Three 35mm Film Frames: Fairground Scenes with Hanging Electric Lights and Children on Swing Set]	1994.253.20	http://www.metmuseum.org/art/collection/search/277023
August (?) 1936	[Three 35mm Film Frames: Two Elderly Men in Conversation on Porch in Front of Painted Sign for "Free Dance", Greensboro, Alabama?]	1994.253.380	http://www.metmuseum.org/art/collection/search/277573
August 1946 (?)	[Three Panel Mirror above Sideboard with Framed Photographs, Estate of Suzette Morton Hamill, Lake Forest, Illinois?]	1994.254.976	http://www.metmuseum.org/art/collection/search/274387
1911	[Three Portrait Snapshots of Walker Evans on Uncut Strip]	1996.166.11	http://www.metmuseum.org/art/collection/search/271984
1930–31	[Tillie Shahn, Truro, Massachusetts]	1994.256.347	http://www.metmuseum.org/art/collection/search/275015
late 1850s–70s	[Unidentified Woman]	2004.545.210	http://www.metmuseum.org/art/collection/search/694909
1860s–80s	[Union League House Philadelphia]	63.350.651.170	http://www.metmuseum.org/art/collection/search/780702
1960s	[View Through Doorway of Standing Girl with Crouching Man Inside]	1998.473.5	http://www.metmuseum.org/art/collection/search/282721
5th century BCE	东周 玉璜|Arc-shaped pendant (Huang)	2009.88a–c	http://www.metmuseum.org/art/collection/search/75281
1917	元禄模様雛形|Genroku moyo hinagata (kosode designs from the Genroku period)	2018.954.7	http://www.metmuseum.org/art/collection/search/74148
ca. 1830–32	冨嶽三十六景　甲州伊沢暁|Dawn at Isawa in Kai Province (Kōshū Isawa no akatsuki), from the series Thirty-six Views of Mount Fuji (Fugaku sanjūrokkei)	JP1328	http://www.metmuseum.org/art/collection/search/55286
8th century	唐 花鳥紋銅鏡|Mirror with birds and flowers	22.141.5	http://www.metmuseum.org/art/collection/search/61399
5th–3rd century BCE	戰國 青銅鳥形器足|Vessel leg in the form of a bird	49.137.3	http://www.metmuseum.org/art/collection/search/61249
dated the 7th month of 1815	清  謝蘭生  山水  軸|Landscape	1986.267.5	http://www.metmuseum.org/art/collection/search/36148
dated 1893	清 虛谷  秋帆圖  冊頁|Sailing in Autumn	1986.267.53	http://www.metmuseum.org/art/collection/search/49468
second half 18th century	清中期  掐絲琺瑯花觚（五供之一）|Vase from a five-piece altar set	29.110.70	http://www.metmuseum.org/art/collection/search/40727
Datable to the 1930s	現代   謝稚柳   臨陳洪綬蛺蝶蓮石圖   鏡片|Butterflies, Bird, Lotus, and Rock, after Chen Hongshou	2005.411.82	http://www.metmuseum.org/art/collection/search/73082
18th–19th century	莫臥兒王朝 鑲金嵌寶玉八棱盒|Box with cover	05.27.1a, b	http://www.metmuseum.org/art/collection/search/58448
late 19th to early 20th century	蟬|Cicada	13.40.209	http://www.metmuseum.org/art/collection/search/43009
ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959
"""

    print("=" * 80)
    print("MET MUSEUM INVENTORY TSV STANDARDIZATION WITH FIXITY PRESERVATION")
    print("=" * 80)
    print(f"Process started: {datetime.now().isoformat()}\n")
    
    # Step 1: Read source and generate source checksums
    print("STEP 1: READING SOURCE FILE AND GENERATING SOURCE CHECKSUMS")
    print("-" * 80)
    rows, source_checksums = read_and_checksum_source(original_content)
    print(f"Total rows read: {len(rows)}")
    print(f"Source file full SHA256: {source_checksums['file_full']}")
    print(f"Generated checksums for {len(source_checksums['rows'])} rows\n")
    
    # Step 2: Standardize
    print("STEP 2: STANDARDIZING DATA")
    print("-" * 80)
    standardized_rows = standardize_rows(rows)
    print(f"Standardization complete: {len(standardized_rows)} rows")
    
    # Count changes by field
    changes = {'date': 0, 'title': 0, 'object_number': 0, 'url': 0}
    for orig, std in zip(rows, standardized_rows):
        if orig.get('Object Date', '') != std.get('Object Date', ''):
            changes['date'] += 1
        if orig.get('Title', '') != std.get('Title', ''):
            changes['title'] += 1
        if orig.get('Object Number', '') != std.get('Object Number', ''):
            changes['object_number'] += 1
        if orig.get('Link Resource', '') != std.get('Link Resource', ''):
            changes['url'] += 1
    
    print(f"  - Date field changes: {changes['date']}")
    print(f"  - Title field changes: {changes['title']}")
    print(f"  - Object Number field changes: {changes['object_number']}")
    print(f"  - URL field changes: {changes['url']}\n")
    
    # Step 3: Write standardized TSV
    print("STEP 3: WRITING STANDARDIZED TSV FILE")
    print("-" * 80)
    output_path = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    write_tsv(standardized_rows, output_path)
    print(f"Wrote to: {output_path}\n")
    
    # Step 4: Read output and generate checksums
    print("STEP 4: GENERATING OUTPUT CHECKSUMS")
    print("-" * 80)
    with open(output_path, 'r', encoding='utf-8') as f:
        output_content = f.read()
    
    output_checksums = generate_output_checksums(standardized_rows, output_content)
    print(f"Output file full SHA256: {output_checksums['file_full']}")
    print(f"Generated checksums for {len(output_checksums['rows'])} rows\n")
    
    # Step 5: Create detailed verification report
    print("STEP 5: CREATING VERIFICATION REPORT")
    print("-" * 80)
    
    verification_report = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'script': 'standardize_met_inventory.py',
            'source_algorithm': 'SHA256',
            'rows_processed': len(rows)
        },
        'source': source_checksums,
        'standardization': {
            'rules_applied': [
                'Trimmed whitespace from all fields',
                'Replaced empty titles with "[Untitled]"',
                'Preserved date format integrity',
                'Validated URL format (must start with http)',
                'Stripped leading/trailing whitespace from object numbers'
            ],
            'changes_by_field': changes
        },
        'output': output_checksums,
        'row_by_row_verification': {}
    }
    
    # Add row-by-row detail
    for idx, (src, std, src_check, out_check) in enumerate(zip(
        rows, standardized_rows,
        source_checksums['rows'].values(),
        output_checksums['rows'].values()
    ), 1):
        verification_report['row_by_row_verification'][idx] = {
            'source_row_hash': src_check['full_row'],
            'output_row_hash': out_check['full_row'],
            'modified': src_check['full_row'] != out_check['full_row'],
            'field_changes': {
                'date': src.get('Object Date', '') != std.get('Object Date', ''),
                'title': src.get('Title', '') != std.get('Title', ''),
                'object_number': src.get('Object Number', '') != std.get('Object Number', ''),
                'url': src.get('Link Resource', '') != std.get('Link Resource', '')
            }
        }
    
    # Write verification report as JSON
    report_path = '/mnt/user-data/outputs/fixity_verification_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(verification_report, f, indent=2, ensure_ascii=False)
    print(f"Verification report written to: {report_path}\n")
    
    # Step 6: Create human-readable summary
    print("STEP 6: CREATING SUMMARY REPORT")
    print("-" * 80)
    
    summary_lines = [
        "MET MUSEUM INVENTORY STANDARDIZATION - SUMMARY REPORT",
        "=" * 80,
        f"Process Timestamp: {datetime.now().isoformat()}",
        "",
        "FILE INFORMATION",
        "-" * 80,
        f"Source file SHA256:  {source_checksums['file_full']}",
        f"Output file SHA256:  {output_checksums['file_full']}",
        f"Total rows: {len(rows)}",
        "",
        "STANDARDIZATION CHANGES",
        "-" * 80,
        f"Rows with title changes:         {changes['title']}",
        f"Rows with date changes:          {changes['date']}",
        f"Rows with object number changes: {changes['object_number']}",
        f"Rows with URL changes:           {changes['url']}",
        "",
        "STANDARDIZATION RULES APPLIED",
        "-" * 80,
        "1. Whitespace: Trimmed leading and trailing whitespace from all fields",
        "2. Titles: Empty title cells replaced with '[Untitled]'",
        "3. Dates: Preserved as-is after whitespace trim (maintains historical accuracy)",
        "4. URLs: Validated format (must start with 'http')",
        "5. Object Numbers: Stripped whitespace, preserved original format",
        "",
        "CHECKSUM COVERAGE",
        "-" * 80,
        f"✓ Full source file: SHA256",
        f"✓ Full output file: SHA256",
        f"✓ Each row in source: SHA256 (canonical JSON representation)",
        f"✓ Each cell in source: SHA256 (by field)",
        f"✓ Each row in output: SHA256 (canonical JSON representation)",
        f"✓ Each cell in output: SHA256 (by field)",
        f"✓ Total data points checksummed: {2 * (1 + len(rows) * 5)} hashes",
        "",
        "OUTPUT FILES",
        "-" * 80,
        f"1. met_inventory_standardized.tsv - Standardized tab-separated values file",
        f"2. fixity_verification_report.json - Detailed verification with all checksums",
        f"3. standardization_summary.txt - This human-readable summary",
        "",
        "HOW TO VERIFY INTEGRITY",
        "-" * 80,
        "1. Compare file checksums in the JSON report to recalculate checksums",
        "2. Examine row-by-row-verification to see which rows were modified",
        "3. Use the cell-level checksums to verify individual data elements",
        "4. The canonical JSON representation ensures field order doesn't affect hashes",
    ]
    
    summary_text = "\n".join(summary_lines)
    summary_path = '/mnt/user-data/outputs/standardization_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_text)
    print(f"Summary written to: {summary_path}\n")
    
    print(summary_text)
    print("\n" + "=" * 80)
    print("STANDARDIZATION COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
