Here's your spreadsheet with **Start Year** and **End Year** columns added. I parsed each "Object Date" value into a numeric range:

- Single years (e.g., "1770") → Start = End = 1770
- "ca." dates → treated as the stated year (e.g., "ca. 1896" → 1896 / 1896)
- Centuries (e.g., "18th century") → 1700 / 1799
- Decade or span ranges (e.g., "1830–40", "1880–92") → start and end years of the span
- BCE dates are shown as negative numbers (e.g., "ca. 600–550 BCE" → -600 / -550)
- Entries with no date → left blank

```csv
Object Date,Start Year,End Year,Title,Artist Display Name,Object Number,Link Resource
ca. 1896,1896,1896,"Street Scene, La-Queue-en-Brie (Val-de-Marne)",Edgar Degas,2000.655.2,http://www.metmuseum.org/art/collection/search/284453
1770,1770,1770,"Sculptura-Historico-Technica: or, the History and Art of Engraving",Filippo Baldinucci|J. Marks,49.25.2,http://www.metmuseum.org/art/collection/search/356878
1912,1912,1912,"Stanage, Detroit, American League, from the Brown Background series (T207) for the American Tobacco Company",American Tobacco Company,63.350.246.207.62,http://www.metmuseum.org/art/collection/search/412476
1766,1766,1766,Mrs. Sylvanus Bourne,John Singleton Copley,24.79,http://www.metmuseum.org/art/collection/search/10533
ca. 600–550 BCE,-600,-550,Terracotta vase in the shape of a bird,,69.11.2,http://www.metmuseum.org/art/collection/search/255277
18th century,1700,1799,,,96.14.454,http://www.metmuseum.org/art/collection/search/66179
1892,1892,1892,D'Orsay #4181,Brewster & Co.,23.112.2539,http://www.metmuseum.org/art/collection/search/745528
6th–7th century,500,699,Fragment of a Cornice,,10.175.19,http://www.metmuseum.org/art/collection/search/456141
,,,Bauhaus Archive,Margarete Willers,"1985.198.92a, b",http://www.metmuseum.org/art/collection/search/484129
ca. 1888,1888,1888,"Miss Baker, from the Actors and Actresses series (N45, Type 1) for Virginia Brights Cigarettes",Allen & Ginter,63.350.203.45.657,http://www.metmuseum.org/art/collection/search/414971
1830–40,1830,1840,"Petits! petits! petits!!!!, from Le Charivari",Delaunois|Aubert et Cie,60.708.150,http://www.metmuseum.org/art/collection/search/822397
16th–17th century,1500,1699,Shaffron (Horse's Head Defense),,36.25.502,http://www.metmuseum.org/art/collection/search/31868
late 19th–early 20th century,1850,1949,Design for single light window,Tiffany Studios|Louis C. Tiffany|Tiffany Glass Company|Tiffany Glass and Decorating Company,67.654.434,http://www.metmuseum.org/art/collection/search/16771
ca. 1763–67,1763,1767,Teapot,Nymphenburg Porcelain Manufactory,"42.205.283a, b",http://www.metmuseum.org/art/collection/search/199295
late 19th–early 20th century,1850,1949,Architectural Ornament with Suspension Hook,,1988.143.100,http://www.metmuseum.org/art/collection/search/316109
ca. 1920,1920,1920,Corpulent Nude Woman,Edward Nagle,1984.433.258,http://www.metmuseum.org/art/collection/search/483397
1563,1563,1563,Cœnotaphiorum (20),Hans Vredeman de Vries|Johannes van Doetecum I|Lucas van Doetecum|Hieronymus Cock,2011.510.20,http://www.metmuseum.org/art/collection/search/402148
ca. 1981–1550 B.C.,-1981,-1550,Spacer (?),,16.7.20,http://www.metmuseum.org/art/collection/search/559404
1771,1771,1771,Ice cream cup (tasse à glace) (one of thirty-one) (part of a service),Sèvres Manufactory,37.20.50,http://www.metmuseum.org/art/collection/search/197875
ca. 1936,1936,1936,Back Street,Michael J. Gallagher|WPA,43.46.91,http://www.metmuseum.org/art/collection/search/374423
mid-5th century BCE,-450,-450,Terracotta fragment of a bell-krater (bowl for mixing wine and water),,2011.604.2.832,http://www.metmuseum.org/art/collection/search/733263
1923,1923,1923,Mountainous Bukhara. Autolithographs in color.,Pavel Kuznetsov|Gosudarstvennoe izdatel'stvo,28.20.9(2),http://www.metmuseum.org/art/collection/search/425888
ca. 1390–1352 B.C.,-1390,-1352,Jar Label,,17.10.475,http://www.metmuseum.org/art/collection/search/563469
1935,1935,1935,"[Brick House with Cast-Iron Porch, New Orleans, Louisiana]",Walker Evans,1994.253.440 (26),http://www.metmuseum.org/art/collection/search/278054
1594,1594,1594,Design for a Cup with a Sea Monster,Friedrich Dürer|Paul Flindt,37.40.5 (13),http://www.metmuseum.org/art/collection/search/776657
1704,1704,1704,Reapers of grain,Giovanni Girolamo Frezza|Carlo Maratti,51.501.2639,http://www.metmuseum.org/art/collection/search/400398
1780–81,1780,1781,Ladle,Hester Bateman,1970.228,http://www.metmuseum.org/art/collection/search/205245
ca. 1830–70,1830,1870,Design for a Brougham,T. Peters and Sons,58.638.301,http://www.metmuseum.org/art/collection/search/841651
3rd–1st century BCE,-299,-1,"Limestone statue of a male votary holding a dove and an apple",,74.51.2725,http://www.metmuseum.org/art/collection/search/242276
530 BCE,-530,-530,Terracotta rim fragment of a kylix: eye-cup (drinking cup),,2011.604.3.2285,http://www.metmuseum.org/art/collection/search/755981
ca. 1540–45,1540,1545,"Polyhymnia, from ""Twelve Muses and Goddesses""",Francesco Primaticcio|Léon Davent,49.97.557,http://www.metmuseum.org/art/collection/search/337119
1829,1829,1829,"A descent from the cross with three other prints, bound in Monuments des Arts du Dessin, volume 2, plate 80",baron Dominique Vivant Denon|Amaury Duval|Brunet|Daniele da Volterra (Daniele Ricciarelli)|Jean-Baptiste Mauzaisse|Taddeo Zuccaro,1994.220(2.19),http://www.metmuseum.org/art/collection/search/645753
19th century,1800,1899,Book cover with overall stripe pattern with geometric designs,Anonymous,48.142.94,http://www.metmuseum.org/art/collection/search/824030
17th century,1600,1699,Length,,66.124.2,http://www.metmuseum.org/art/collection/search/229151
1st century BC,-99,-1,Statue of Horwedja,,06.1232.27,http://www.metmuseum.org/art/collection/search/571624
"1811, (Bunka 8); 1817",1811,1817,,Tani Bunchō 谷文晁,2013.664,http://www.metmuseum.org/art/collection/search/78585
1975–76,1975,1976,Dress,Geoffrey Beene,2001.393.23,http://www.metmuseum.org/art/collection/search/82724
early 20th century,1900,1930,Cap,,1976.390.40,http://www.metmuseum.org/art/collection/search/103319
1785–90,1785,1790,Cream Pitcher,,10.149.240,http://www.metmuseum.org/art/collection/search/2711
late 16th–early 17th century,1575,1649,Story of Phaeton,Guglielmo della Porta,13.94.1,http://www.metmuseum.org/art/collection/search/192329
17th century,1600,1699,Piece,,41.100.48a,http://www.metmuseum.org/art/collection/search/226578
,,,The Annunciation,Budapest Master,58.145.1,http://www.metmuseum.org/art/collection/search/435822
1850,1850,1850,Stags in Woods,Charles-François Daubigny,23.65.48,http://www.metmuseum.org/art/collection/search/336862
1880–92,1880,1892,"Violet Cameron, from the Actors and Actresses series (N342), Type 3a, issued by Thomas H. Hall Tobacco to promote Between the Acts Cigarettes.","Thomas H. Hall Tobacco|Lindner, Eddy & Claus",63.350.223.342.321,http://www.metmuseum.org/art/collection/search/660866
ca. 3800–3300 BCE,-3800,-3300,Terracotta rim of a bowl,,30.119.35,http://www.metmuseum.org/art/collection/search/253240
1985,1985,1985,Baritone Violin,Carleen M. Hutchins|Rafael Bronstein,1988.424.6,http://www.metmuseum.org/art/collection/search/503355
19th century,1800,1899,Sheet with overall pattern of flowers and dots,Anonymous,48.142.89,http://www.metmuseum.org/art/collection/search/823744
1879,1879,1879,Preparatory Drawing for an Illustration of a Seventeenth-Century Dutch Tankard from the Demidov Collection,C. Prosdocimi,32.103.7,http://www.metmuseum.org/art/collection/search/346108
mid-19th century,1840,1860,Cuffs,,"2009.300.1841a, b",http://www.metmuseum.org/art/collection/search/156601
probably after 1657,1657,1700,Watch,David Buschman,17.190.1516,http://www.metmuseum.org/art/collection/search/194109
```

**Notes on judgment calls:**
- **"Early"/"mid"/"late" centuries** were given approximate spans (e.g., "late 16th–early 17th century" → 1575–1649; "mid-19th century" → 1840–1860).
- **"Probably after 1657"** → Start 1657, End 1700 as a working upper bound.
- **"ca. 1981–1550 B.C."** appears to be a typo in the source (the start is later than the end in the original ordering), so I entered -1981 / -1550 as written; you may want to verify it.
- **"3rd–1st century BCE"** → -299 / -1, reflecting the span from 300 BCE to 1 BCE.
- Rows with no date are left blank in both new columns.