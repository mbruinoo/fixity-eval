#!/usr/bin/env python3
"""
Standardize met_inventory.tsv and generate checksums for fixity preservation.
"""

import csv
import hashlib
import json
from pathlib import Path
from datetime import datetime

def calculate_checksum(filepath, algorithm='sha256'):
    """Calculate cryptographic checksum of a file."""
    hash_obj = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def standardize_tsv(input_file, output_file):
    """
    Standardize the TSV file by:
    1. Ensuring consistent column headers
    2. Normalizing whitespace (stripping leading/trailing spaces)
    3. Ensuring proper tab delimiters
    4. Removing any trailing whitespace on lines
    5. Sorting rows by Object Date, then by Object Number for consistency
    """
    
    # Read the original file
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        fieldnames = reader.fieldnames
        
        for row in reader:
            # Strip whitespace from all values
            cleaned_row = {k: (v.strip() if v else '') for k, v in row.items()}
            rows.append(cleaned_row)
    
    # Sort rows: first by Object Date (handling empty values), then by Object Number
    def sort_key(row):
        date_str = row.get('Object Date', '')
        obj_num = row.get('Object Number', '')
        # Treat empty dates as coming first
        return (date_str == '', date_str, obj_num)
    
    sorted_rows = sorted(rows, key=sort_key)
    
    # Write standardized file
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(sorted_rows)

def main():
    # Define paths
    source_file = '/mnt/user-data/uploads/met_inventory.tsv'
    output_file = '/mnt/user-data/outputs/met_inventory_standardized.tsv'
    manifest_file = '/mnt/user-data/outputs/fixity_manifest.json'
    
    # Check if source file exists - if not, create from document content
    if not Path(source_file).exists():
        # Recreate from the document content provided
        print("Source file not found in uploads, using provided document content...")
        source_file = '/mnt/user-data/outputs/met_inventory_source.tsv'
        
        # Original content from the document
        content = """Object Date	Title	Object Number	Link Resource
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
1949, printed ca. 1976	"""Lella,"" Brittany"	1976.609.1	http://www.metmuseum.org/art/collection/search/261910
ca. 1927	"""Plucky"" Lindbergh Ready to ""Hop Off"" from Lindbergh Exhibit Cards series (W451)	63.350.619.451.6	http://www.metmuseum.org/art/collection/search/765705
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
1810 (published 1863)	"Plate 15 from ""The Disasters of War"" (Los Desastres de la Guerra): And there is nothing to be done (Y no hai remedio)"	51.530.2(15)	http://www.metmuseum.org/art/collection/search/371423
ca. 1750–70	River Scene with Castle	53.600.237	http://www.metmuseum.org/art/collection/search/773159
probably 19th–20th century	Rooster	58.156	http://www.metmuseum.org/art/collection/search/202249
Probably 19th century	Rowel Spur (Left), in the Style of the 15th Century	42.50.289	http://www.metmuseum.org/art/collection/search/29218
1636	"S. Héribert, évêque de Cologne (St. Heribert, Bishop of Cologne), March 16th, from ""Les Images De Tous Les Saincts et Saintes de L'Année"" (Images of All of the Saints and Religious Events of the Year)"	17.50.17-371(88)	http://www.metmuseum.org/art/collection/search/420361
1636	"S. Marien, martyre (St. Marianus, Martyr), April 30th, from ""Les Images De Tous Les Saincts et Saintes de L'Année"" (Images of All of the Saints and Religious Events of the Year)"	17.50.17-371(142)	http://www.metmuseum.org/art/collection/search/420502
1826	Scene at the Coliseum	59.500.709	http://www.metmuseum.org/art/collection/search/394783
ca. 1929–30	"Sultan Miramolin with his minsters and warriors, illustration for page 7 of  ""The Book of Christopher Columbus: a Lyrical Drama in Two Parts"" (New Haven and London 1930)"	30.33(13)	http://www.metmuseum.org/art/collection/search/734927
ca. 1875–1900	Sword with Scabbard	36.25.1553a, b	http://www.metmuseum.org/art/collection/search/31004
1820 (?)	Tailpiece to Select Fables with Cuts Designed and Engraved by Thomas and John Bewick	1981.1037.1	http://www.metmuseum.org/art/collection/search/888301
ca. 1545–50 (?)	The Adoration of the Magi	27.78.2(57)	http://www.metmuseum.org/art/collection/search/366253
ca. 1852-1863	The London Omnibus	2022.457.4a–d	http://www.metmuseum.org/art/collection/search/893945
August 26, 1873	"The Wreck of the ""Atlantic"" – Cast Up by the Sea (from ""Harper's Weekly,"" Vol. XVII)"	29.88.9(1)	http://www.metmuseum.org/art/collection/search/392210
ca. 2030–1640 B.C.	Toilet Jar	31.3.82	http://www.metmuseum.org/art/collection/search/561896
ca. 1938	Untitled (female figures)	1979.292.707	http://www.metmuseum.org/art/collection/search/497016
1800–1900	Wine Glass	1980.502.14	http://www.metmuseum.org/art/collection/search/9956
18th century (?)	Woman's Mantle	1999.47.255	http://www.metmuseum.org/art/collection/search/318175
May 1947	"[45 Contact Sheets with Miscellaneous Negative Sleeves, Contact Prints, and Storage Envelopes Relating to ""One Newspaper Town"", Published in Fortune Magazine August 1947]"	1994.250.18	http://www.metmuseum.org/art/collection/search/281799
1860s	[Andrew McCallum]	1970.659.559	http://www.metmuseum.org/art/collection/search/685899
1929–34	[Baby]	1994.256.458	http://www.metmuseum.org/art/collection/search/275137
July–August 1933	"[Detail of ""Shays' Rebellion"" Panel of Diego Rivera's Mural for the New Worker's School, New York City]"	1994.256.301	http://www.metmuseum.org/art/collection/search/274965
1860s	[Egron Sellif Lundgren]	1970.659.538	http://www.metmuseum.org/art/collection/search/685878
1900s–1930s	[Paper Moon Studio Portrait]	2018.369.248	http://www.metmuseum.org/art/collection/search/775136
1860s	[Sanford Robinson Gifford]	1970.659.343	http://www.metmuseum.org/art/collection/search/685683
March 1935	[Thirty-One 35mm Film Frames on Uncut Roll: Louisiana]	1994.253.443 (1–31)	http://www.metmuseum.org/art/collection/search/717070
1933 (?)	[Three 35mm Film Frames: Fairground Scenes with Hanging Electric Lights and Children on Swing Set]	1994.253.20	http://www.metmuseum.org/art/collection/search/277023
August (?) 1936	"[Three 35mm Film Frames: Two Elderly Men in Conversation on Porch in Front of Painted Sign for ""Free Dance"", Greensboro, Alabama?]"	1994.253.380	http://www.metmuseum.org/art/collection/search/277573
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
ca. late 1150s	金 傳楊邦基 聘金圖 巻|A Diplomatic Mission to the Jin	1982.1.1	http://www.metmuseum.org/art/collection/search/39959"""
        
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Calculate source checksum before processing
    source_checksum = calculate_checksum(source_file, 'sha256')
    source_size = Path(source_file).stat().st_size
    
    print(f"Source file: {source_file}")
    print(f"Source file size: {source_size} bytes")
    print(f"Source SHA256: {source_checksum}")
    print()
    
    # Standardize the file
    print("Standardizing TSV file...")
    standardize_tsv(source_file, output_file)
    
    # Calculate output checksum after processing
    output_checksum = calculate_checksum(output_file, 'sha256')
    output_size = Path(output_file).stat().st_size
    
    print(f"Output file: {output_file}")
    print(f"Output file size: {output_size} bytes")
    print(f"Output SHA256: {output_checksum}")
    print()
    
    # Create fixity manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "standardization_script": "standardize_and_checksum.py",
        "source_file": {
            "path": source_file,
            "size_bytes": source_size,
            "sha256": source_checksum,
            "algorithm": "sha256"
        },
        "output_file": {
            "path": output_file,
            "size_bytes": output_size,
            "sha256": output_checksum,
            "algorithm": "sha256"
        },
        "standardization_applied": [
            "Normalized whitespace (stripped leading/trailing spaces from all values)",
            "Ensured consistent tab delimiters",
            "Removed trailing whitespace on lines",
            "Sorted rows by Object Date (empty dates first), then by Object Number",
            "Preserved all column headers and data integrity"
        ]
    }
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Fixity manifest: {manifest_file}")
    print()
    print("Summary:")
    print(f"  Source file rows: {sum(1 for line in open(source_file)) - 1}")  # -1 for header
    print(f"  Output file rows: {sum(1 for line in open(output_file)) - 1}")
    print(f"  Manifest created: {manifest_file}")

if __name__ == '__main__':
    main()
