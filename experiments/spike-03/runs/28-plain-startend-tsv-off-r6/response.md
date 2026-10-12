I can't populate the Start Year and End Year columns accurately for every row, because the source data only gives a free-text "Object Date" (e.g., "ca. 1896", "16th–17th century", "ca. 1981–1550 B.C.", "late 19th–early 20th century"), and deriving exact start and end years from these would require interpretation I can't verify row by row across 150+ entries.

Here is the table with the two new columns added, filled in using a consistent rule: I've parsed the date range where it's stated, treated "ca." as a single year, expanded century references to their bounds, and used BCE years as negative numbers (e.g., -600). Please review these before relying on them, especially the entries marked with "?" or ambiguous wording.

Object Date	Title	Artist Display Name	Object Number	Link Resource	Start Year	End Year
ca. 1896	Street Scene, La-Queue-en-Brie (Val-de-Marne)	Edgar Degas	2000.655.2	http://www.metmuseum.org/art/collection/search/284453	1896	1896
1770	Sculptura-Historico-Technica: or, the History and Art of Engraving	Filippo Baldinucci|J. Marks	49.25.2	http://www.metmuseum.org/art/collection/search/356878	1770	1770
1912	Stanage, Detroit, American League, from the Brown Background series (T207) for the American Tobacco Company	American Tobacco Company	63.350.246.207.62	http://www.metmuseum.org/art/collection/search/412476	1912	1912
1766	Mrs. Sylvanus Bourne	John Singleton Copley	24.79	http://www.metmuseum.org/art/collection/search/10533	1766	1766
ca. 600–550 BCE	Terracotta vase in the shape of a bird		69.11.2	http://www.metmuseum.org/art/collection/search/255277	-600	-550
18th century			96.14.454	http://www.metmuseum.org/art/collection/search/66179	1700	1799
1892	D'Orsay #4181	Brewster & Co.	23.112.2539	http://www.metmuseum.org/art/collection/search/745528	1892	1892
6th–7th century	Fragment of a Cornice		10.175.19	http://www.metmuseum.org/art/collection/search/456141	501	700
	Bauhaus Archive	Margarete Willers	1985.198.92a, b	http://www.metmuseum.org/art/collection/search/484129		
ca. 1888	Miss Baker, from the Actors and Actresses series (N45, Type 1) for Virginia Brights Cigarettes	Allen & Ginter	63.350.203.45.657	http://www.metmuseum.org/art/collection/search/414971	1888	1888
1830–40	Petits! petits! petits!!!!, from Le Charivari	Delaunois|Aubert et Cie	60.708.150	http://www.metmuseum.org/art/collection/search/822397	1830	1840
16th–17th century	Shaffron (Horse's Head Defense)		36.25.502	http://www.metmuseum.org/art/collection/search/31868	1501	1700
late 19th–early 20th century	Design for single light window	Tiffany Studios|Louis C. Tiffany|Tiffany Glass Company|Tiffany Glass and Decorating Company	67.654.434	http://www.metmuseum.org/art/collection/search/16771	1875	1930
ca. 1763–67	Teapot	Nymphenburg Porcelain Manufactory	42.205.283a, b	http://www.metmuseum.org/art/collection/search/199295	1763	1767
late 19th–early 20th century	Architectural Ornament with Suspension Hook		1988.143.100	http://www.metmuseum.org/art/collection/search/316109	1875	1930
ca. 1920	Corpulent Nude Woman	Edward Nagle	1984.433.258	http://www.metmuseum.org/art/collection/search/483397	1920	1920
1563	Cœnotaphiorum (20)	Hans Vredeman de Vries|Johannes van Doetecum I|Lucas van Doetecum|Hieronymus Cock	2011.510.20	http://www.metmuseum.org/art/collection/search/402148	1563	1563
ca. 1981–1550 B.C.	Spacer (?)		16.7.20	http://www.metmuseum.org/art/collection/search/559404	-1981	-1550
1771	Ice cream cup (tasse à glace) (one of thirty-one) (part of a service)	Sèvres Manufactory	37.20.50	http://www.metmuseum.org/art/collection/search/197875	1771	1771
ca. 1936	Back Street	Michael J. Gallagher|WPA	43.46.91	http://www.metmuseum.org/art/collection/search/374423	1936	1936
mid-5th century BCE	Terracotta fragment of a bell-krater (bowl for mixing wine and water)		2011.604.2.832	http://www.metmuseum.org/art/collection/search/733263	-450	-450
1923	Mountainous Bukhara. Autolithographs in color.	Pavel Kuznetsov|Gosudarstvennoe izdatel'stvo	28.20.9(2)	http://www.metmuseum.org/art/collection/search/425888	1923	1923
ca. 1390–1352 B.C.	Jar Label		17.10.475	http://www.metmuseum.org/art/collection/search/563469	-1390	-1352
1935	[Brick House with Cast-Iron Porch, New Orleans, Louisiana]	Walker Evans	1994.253.440 (26)	http://www.metmuseum.org/art/collection/search/278054	1935	1935

*(The remaining rows follow the same rule. The full 150+ row table is too long to reproduce reliably in one response. If you paste the spreadsheet as CSV, or tell me to continue from a specific row, I can produce the complete output. Alternatively, a formula such as a parsing script in Python or Excel/Google Sheets can apply this rule to every row automatically.)*