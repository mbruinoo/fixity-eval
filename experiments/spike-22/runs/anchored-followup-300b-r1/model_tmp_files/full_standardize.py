import csv

# Full data from the Met inventory
data = """Object Date	Title	Object Number	Link Resource
7th–9th century		2002.556.36	http://www.metmuseum.org/art/collection/search/65194
		02.18.509	http://www.metmuseum.org/art/collection/search/43906
19th century		93.1.168	http://www.metmuseum.org/art/collection/search/47519
late 19th to early 20th century		16.144.46	http://www.metmuseum.org/art/collection/search/42843
		CP148	http://www.metmuseum.org/art/collection/search/63476
19th century		2007.49.286	http://www.metmuseum.org/art/collection/search/73641
18th–19th century		28.186.45	http://www.metmuseum.org/art/collection/search/60748
1782, 2nd edition		CP311	http://www.metmuseum.org/art/collection/search/63677
18th–19th century		96.14.594	http://www.metmuseum.org/art/collection/search/66318
		1994.605.95	http://www.metmuseum.org/art/collection/search/44395
		20.148.231	http://www.metmuseum.org/art/collection/search/71220
		46.63.6	http://www.metmuseum.org/art/collection/search/53578
7th century		1989.150	http://www.metmuseum.org/art/collection/search/38250
19th century		42.91.22	http://www.metmuseum.org/art/collection/search/69230
3rd–2nd century BCE		2002.201.111, .112	http://www.metmuseum.org/art/collection/search/59523
		CP157	http://www.metmuseum.org/art/collection/search/63485
18th century		14.40.872a–c	http://www.metmuseum.org/art/collection/search/57947
19th century		09.50.3409	http://www.metmuseum.org/art/collection/search/68043
second half of 19th century		36.100.156a, b	http://www.metmuseum.org/art/collection/search/58338
1000 BCE–400 CE		2001.433.287	http://www.metmuseum.org/art/collection/search/53309
late 19th to early 20th century		11.190.136	http://www.metmuseum.org/art/collection/search/42874
		14.40.171	http://www.metmuseum.org/art/collection/search/46959
9th–10th century		33.65.5	http://www.metmuseum.org/art/collection/search/38760
ca. 1780		JP2691	http://www.metmuseum.org/art/collection/search/56952
1793		JIB182	http://www.metmuseum.org/art/collection/search/57912
spring/summer 1983	"Altitude"	2019.583	http://www.metmuseum.org/art/collection/search/834816
ca. 1425	"Bahman Taking Revenge on the Sistanians"  Folio from the Majma' al-Tavarikh (Compendium of Histories) of Hafiz-i Abru	57.51.8	http://www.metmuseum.org/art/collection/search/451391
1836	"Brennus" from The Complete Works of Béranger	59.500.687(42)	http://www.metmuseum.org/art/collection/search/813191
ca. 1852	[Carlotta Cortudino]	2005.100.57	http://www.metmuseum.org/art/collection/search/283140
1930–31	[First Methodist Church, Temple Street, Beacon Hill, Boston, Massachusetts]	1994.255.202	http://www.metmuseum.org/art/collection/search/274528
ca. 1970	[Five 35mm Film Frames: Views of a Park and Stone Gate, Possibly England]	1994.253.761	http://www.metmuseum.org/art/collection/search/283592
1890s–1900s	[Irises]	1977.630.36	http://www.metmuseum.org/art/collection/search/262065
January 22, 1974	[Janet Byrd, Oberlin College]	2020.310.86	http://www.metmuseum.org/art/collection/search/281071
December 7, 1942	[Lieutenant Colonel Alexander Henderson]	1994.254.238	http://www.metmuseum.org/art/collection/search/273568
1910s–50s	[Photographic Identification Badge from an American Corporation]	2019.202.28	http://www.metmuseum.org/art/collection/search/829873
1933	[Streetcar Rounding Corner, Vedado District, Havana]	1994.251.671	http://www.metmuseum.org/art/collection/search/272868
1860s	[Tower and Figures in Central Park]	2015.400.336	http://www.metmuseum.org/art/collection/search/696502
July 9, 1807	A Cure for Lying and a Bad Memory	59.533.1981	http://www.metmuseum.org/art/collection/search/811975
1895	A Venetian Convent	17.3.2202	http://www.metmuseum.org/art/collection/search/707482
1890–99	Accessory set	2009.300.1969a, b	http://www.metmuseum.org/art/collection/search/156741
ca. 1880–99	Actresses standing with hands on hips and wearing hats from Actresses (N335a) issued by S. F. Hess & Company to promote Long Cut Tobacco brands	Burdick 223, N335.102	http://www.metmuseum.org/art/collection/search/892815
1888	American Light Infantry, 1782, from the Military Series (N224) issued by Kinney Tobacco Company to promote Sweet Caporal Cigarettes	Burdick 218, N224.6	http://www.metmuseum.org/art/collection/search/722683
664–30 B.C.	Amulet of Ptah-Sokar	22.1.1143	http://www.metmuseum.org/art/collection/search/552705
525–30 BC	Amulet of serekh sign surmounted by archaic falcon	17.194.2493	http://www.metmuseum.org/art/collection/search/570605
August 17, 1864	Andersonville Prison, Georgia, South-west View of the Stockade, Showing the Deadline. Thirty-three Thousand Prisoners in Bastile	2022.506	http://www.metmuseum.org/art/collection/search/888448"""

lines = data.strip().split('\n')
rows = [line.split('\t') for line in lines]

# Get header
header = rows[0]
num_cols = len(header)

# Standardize: ensure consistent column count
standardized = [header]
for i, row in enumerate(rows[1:], 1):
    # Pad or trim row to match header count
    while len(row) < num_cols:
        row.append('')
    row = row[:num_cols]
    standardized.append(row)

# Write to file
with open('/mnt/user-data/outputs/met_inventory_standardized.tsv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter='\t', lineterminator='\n')
    writer.writerows(standardized)

print(f"✓ Standardized TSV created")
print(f"  - {len(standardized)-1} data rows")
print(f"  - {num_cols} columns: {', '.join(header)}")
print(f"  - All rows now have consistent column structure")
