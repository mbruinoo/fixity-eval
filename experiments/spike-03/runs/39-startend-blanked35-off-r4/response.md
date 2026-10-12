I can't open a file directly, but here is your data with **Start Year** and **End Year** columns added. I derived them from the "Object Date" column as follows:

- **Exact years** (e.g., "1770") → Start Year = End Year = that year
- **"ca." dates** (e.g., "ca. 1896") → the year, for both columns
- **Ranges** (e.g., "1850s", "late 19th century", "16th–17th century") → the bounding years
- **BCE dates** → negative numbers (e.g., 1st century BC → -100 to -1)
- **Missing or unknown dates** → left blank

Because the source contains many approximate and descriptive dates, these values are reasonable estimates rather than verified dates. Note that "ca. 1981–1550 B.C." appears to be a typo in the source; I've interpreted it as -1981 to -1550.

```csv
Object Date,Title,Artist Display Name,Object Number,Link Resource,Start Year,End Year
ca. 1896,"Street Scene, La-Queue-en-Brie (Val-de-Marne)",Edgar Degas,2000.655.2,http://www.metmuseum.org/art/collection/search/284453,1896,1896
1770,"Sculptura-Historico-Technica: or, the History and Art of Engraving",Filippo Baldinucci|J. Marks,49.25.2,http://www.metmuseum.org/art/collection/search/356878,1770,1770
1912,"Stanage, Detroit, American League, from the Brown Background series (T207) for the American Tobacco Company",American Tobacco Company,63.350.246.207.62,http://www.metmuseum.org/art/collection/search/412476,1912,1912
1766,Mrs. Sylvanus Bourne,John Singleton Copley,24.79,http://www.metmuseum.org/art/collection/search/10533,1766,1766
,Terracotta vase in the shape of a bird,,69.11.2,http://www.metmuseum.org/art/collection/search/255277,,
,,,96.14.454,http://www.metmuseum.org/art/collection/search/66179,,
,D'Orsay #4181,Brewster & Co.,23.112.2539,http://www.metmuseum.org/art/collection/search/745528,,
,Fragment of a Cornice,,10.175.19,http://www.metmuseum.org/art/collection/search/456141,,
,Bauhaus Archive,Margarete Willers,"1985.198.92a, b",http://www.metmuseum.org/art/collection/search/484129,,
,"Miss Baker, from the Actors and Actresses series (N45, Type 1) for Virginia Brights Cigarettes",Allen & Ginter,63.350.203.45.657,http://www.metmuseum.org/art/collection/search/414971,,
,"Petits! petits! petits!!!!, from Le Charivari",Delaunois|Aubert et Cie,60.708.150,http://www.metmuseum.org/art/collection/search/822397,,
16th–17th century,Shaffron (Horse's Head Defense),,36.25.502,http://www.metmuseum.org/art/collection/search/31868,1500,1700
,Design for single light window,Tiffany Studios|Louis C. Tiffany|Tiffany Glass Company|Tiffany Glass and Decorating Company,67.654.434,http://www.metmuseum.org/art/collection/search/16771,,
,Teapot,Nymphenburg Porcelain Manufactory,"42.205.283a, b",http://www.metmuseum.org/art/collection/search/199295,,
late 19th–early 20th century,Architectural Ornament with Suspension Hook,,1988.143.100,http://www.metmuseum.org/art/collection/search/316109,1875,1925
ca. 1920,Corpulent Nude Woman,Edward Nagle,1984.433.258,http://www.metmuseum.org/art/collection/search/483397,1920,1920
,Cœnotaphiorum (20),Hans Vredeman de Vries|Johannes van Doetecum I|Lucas van Doetecum|Hieronymus Cock,2011.510.20,http://www.metmuseum.org/art/collection/search/402148,,
ca. 1981–1550 B.C.,Spacer (?),,16.7.20,http://www.metmuseum.org/art/collection/search/559404,-1981,-1550
,Ice cream cup (tasse à glace) (one of thirty-one) (part of a service),Sèvres Manufactory,37.20.50,http://www.metmuseum.org/art/collection/search/197875,,
ca. 1936,Back Street,Michael J. Gallagher|WPA,43.46.91,http://www.metmuseum.org/art/collection/search/374423,1936,1936
,Terracotta fragment of a bell-krater (bowl for mixing wine and water),,2011.604.2.832,http://www.metmuseum.org/art/collection/search/733263,,
1923,Mountainous Bukhara. Autolithographs in color.,Pavel Kuznetsov|Gosudarstvennoe izdatel'stvo,28.20.9(2),http://www.metmuseum.org/art/collection/search/425888,1923,1923
ca. 1390–1352 B.C.,Jar Label,,17.10.475,http://www.metmuseum.org/art/collection/search/563469,-1390,-1352
1935,"[Brick House with Cast-Iron Porch, New Orleans, Louisiana]",Walker Evans,1994.253.440 (26),http://www.metmuseum.org/art/collection/search/278054,1935,1935
1594,Design for a Cup with a Sea Monster,Friedrich Dürer|Paul Flindt,37.40.5 (13),http://www.metmuseum.org/art/collection/search/776657,1594,1594
1704,Reapers of grain,Giovanni Girolamo Frezza|Carlo Maratti,51.501.2639,http://www.metmuseum.org/art/collection/search/400398,1704,1704
1780–81,Ladle,Hester Bateman,1970.228,http://www.metmuseum.org/art/collection/search/205245,1780,1781
,Design for a Brougham,T. Peters and Sons,58.638.301,http://www.metmuseum.org/art/collection/search/841651,,
,Limestone statue of a male votary holding a dove and an apple,,74.51.2725,http://www.metmuseum.org/art/collection/search/242276,,
,Terracotta rim fragment of a kylix: eye-cup (drinking cup),,2011.604.3.2285,http://www.metmuseum.org/art/collection/search/755981,,
ca. 1540–45,"Polyhymnia, from ""Twelve Muses and Goddesses""",Francesco Primaticcio|Léon Davent,49.97.557,http://www.metmuseum.org/art/collection/search/337119,1540,1545
,"A descent from the cross with three other prints, bound in Monuments des Arts du Dessin, volume 2, plate 80",baron Dominique Vivant Denon|Amaury Duval|Brunet|Daniele da Volterra (Daniele Ricciarelli)|Jean-Baptiste Mauzaisse|Taddeo Zuccaro,1994.220(2.19),http://www.metmuseum.org/art/collection/search/645753,,
19th century,Book cover with overall stripe pattern with geometric designs,Anonymous,48.142.94,http://www.metmuseum.org/art/collection/search/824030,1800,1899
17th century,Length,,66.124.2,http://www.metmuseum.org/art/collection/search/229151,1600,1699
1st century BC,Statue of Horwedja,,06.1232.27,http://www.metmuseum.org/art/collection/search/571624,-100,-1
"1811, (Bunka 8); 1817",,Tani Bunchō 谷文晁,2013.664,http://www.metmuseum.org/art/collection/search/78585,1811,1817
1975–76,Dress,Geoffrey Beene,2001.393.23,http://www.metmuseum.org/art/collection/search/82724,1975,1976
early 20th century,Cap,,1976.390.40,http://www.metmuseum.org/art/collection/search/103319,1900,1930
,Cream Pitcher,,10.149.240,http://www.metmuseum.org/art/collection/search/2711,,
late 16th–early 17th century,Story of Phaeton,Guglielmo della Porta,13.94.1,http://www.metmuseum.org/art/collection/search/192329,1575,1625
17th century,Piece,,41.100.48a,http://www.metmuseum.org/art/collection/search/226578,1600,1699
,The Annunciation,Budapest Master,58.145.1,http://www.metmuseum.org/art/collection/search/435822,,
1850,Stags in Woods,Charles-François Daubigny,23.65.48,http://www.metmuseum.org/art/collection/search/336862,1850,1850
,"Violet Cameron, from the Actors and Actresses series (N342), Type 3a, issued by Thomas H. Hall Tobacco to promote Between the Acts Cigarettes.","Thomas H. Hall Tobacco|Lindner, Eddy & Claus",63.350.223.342.321,http://www.metmuseum.org/art/collection/search/660866,,
ca. 3800–3300 BCE,Terracotta rim of a bowl,,30.119.35,http://www.metmuseum.org/art/collection/search/253240,-3800,-3300
1985,Baritone Violin,Carleen M. Hutchins|Rafael Bronstein,1988.424.6,http://www.metmuseum.org/art/collection/search/503355,1985,1985
19th century,Sheet with overall pattern of flowers and dots,Anonymous,48.142.89,http://www.metmuseum.org/art/collection/search/823744,1800,1899
1879,Preparatory Drawing for an Illustration of a Seventeenth-Century Dutch Tankard from the Demidov Collection,C. Prosdocimi,32.103.7,http://www.metmuseum.org/art/collection/search/346108,1879,1879
,Cuffs,,"2009.300.1841a, b",http://www.metmuseum.org/art/collection/search/156601,,
probably after 1657,Watch,David Buschman,17.190.1516,http://www.metmuseum.org/art/collection/search/194109,1657,
,清 碧璽花卉紋佩件|Pendant with floral designs,,21.175.127,http://www.metmuseum.org/art/collection/search/43344,,
1982,Westruckness,Ardeshir Mohassess,2018.617.2.8,http://www.metmuseum.org/art/collection/search/850725,1982,1982
1915,L'Exode Serbe,Théophile-Alexandre Steinlen,68.785.31,http://www.metmuseum.org/art/collection/search/726014,1915,1915
,"Eight fragments of a terracotta kylix, joining 12.231.2",Onesimos|Euphronios,1971.54,http://www.metmuseum.org/art/collection/search/255336,,
16th century,,,46.186.14,http://www.metmuseum.org/art/collection/search/50541,1500,1599
16th century,Piece,,09.50.1632,http://www.metmuseum.org/art/collection/search/216655,1500,1599
,Shoes,Gösta,"2009.300.5889a, b",http://www.metmuseum.org/art/collection/search/170299,,
,"Etiévant. Henri, Achille. 32 ans, né à Flammanville (Manche). Typographe. Anarchiste. 4/3/94.",Alphonse Bertillon,2005.100.375.160,http://www.metmuseum.org/art/collection/search/306783,,
,"Beach Scene at Beg Meil, Brittany",Alice P. Shurtleff,51.77,http://www.metmuseum.org/art/collection/search/488672,,
1853–56,The Lonely Glen,John Dillwyn Llewelyn,2005.100.382 (31),http://www.metmuseum.org/art/collection/search/287921,1853,1856
unknown,Brocade,,12.49.7,http://www.metmuseum.org/art/collection/search/446209,,
1960s,Romanesque Christs (XIth and XIIth centuries),Jean Dieuzaide,65.609.3,http://www.metmuseum.org/art/collection/search/271011,1960,1969
19th century,Chinese Paintings: Fish,"Anonymous, Japanese, 19th Century",1970.565.464,http://www.metmuseum.org/art/collection/search/347519,1800,1899
1647,Pietro Aretino,Pietro Aretino|Marcantonio Raimondi|Titian (Tiziano Vecellio)|Wenceslaus Hollar,17.3.756-1357,http://www.metmuseum.org/art/collection/search/360636,1647,1647
1950,Paper cover for Callahan Hall of Fame Baseball cards (W576),"B.E. Callahan, Publisher","Burdick 537, W576.1",http://www.metmuseum.org/art/collection/search/824803,1950,1950
,Statuette of a warrior-11,,24.195.72,http://www.metmuseum.org/art/collection/search/251638,,
1624,"Saint Vitalis, from Bavaria Sancta: The Life and Martyrdom of Holy Men and Women (Vol. II)",Raphael Sadeler II|Matthaeus Rader,53.601.13(70),http://www.metmuseum.org/art/collection/search/716514,1624,1624
1282–85,Ducat of Constance of Aragon (1282-1285),,67.265.18,http://www.metmuseum.org/art/collection/search/468729,1282,1285
,"Manita, Ahmedabad, India",Fazal Sheikh,2008.398,http://www.metmuseum.org/art/collection/search/289126,,
ca. 1960,Toque,Cristobal Balenciaga|House of Balenciaga,2009.300.8364,http://www.metmuseum.org/art/collection/search/175375,1960,1960
late 19th century,Design for a Cabinet,Charles E. King,54.509.76,http://www.metmuseum.org/art/collection/search/409116,1875,1899
460–440 BCE,Terracotta rim fragment of a kylix (drinking cup),,2011.604.1.4032,http://www.metmuseum.org/art/collection/search/693590,-460,-440
,Tumbler,,1980.502.17,http://www.metmuseum.org/art/collection/search/9130,,
18th century,"Trade Card for William Sharp, Engraver",William Sharp,26.28.240,http://www.metmuseum.org/art/collection/search/817340,1700,1799
,王鐸  行書臨虞世南《賢兄》帖 扇頁|Letter by Yu Shinan (558-638),Wang Duo,1989.363.115,http://www.metmuseum.org/art/collection/search/49025,,
1768,"絵本雪月花; 絵本倭文庫(えほんやまとぶんこ)|Picture Book of Snow, Moon, and Flowers (Ehon setsugekka) 絵本雪月花; 絵本倭文庫(えほんやまとぶんこ)",Nishikawa Sukenobu 西川祐信,2013.840,http://www.metmuseum.org/art/collection/search/78730,1768,1768
,The Banquet for the Return of the Prodigal Son,Anonymous|Abraham Bosse|Jean I Leblond,51.501.2294,http://www.metmuseum.org/art/collection/search/386092,,
,Dress,Jeanne Victorine Margaine-Lacroix|Maison Margaine-Lacroix,1979.346.32,http://www.metmuseum.org/art/collection/search/83566,,
,Pico de Orizaba,Hugo Brehme,1987.1144.17,http://www.metmuseum.org/art/collection/search/265691,,
,清/現代　莊曜孚　紅荷圖　摺扇|Lotus,Zhuang Yaofu,1986.267.161,http://www.metmuseum.org/art/collection/search/36232,,
n.d.,Portrait of Gaetano Filangieri,Jean-Baptiste-François Bosio,49.19.111,http://www.metmuseum.org/art/collection/search/334841,,
late 18th century,Woodblock,Swaislands Fabric Printing Works,"27.247.3a, b",http://www.metmuseum.org/art/collection/search/222130,1775,1799
1841,William Huntington of New York,Auguste Edouart,50.602.1080,http://www.metmuseum.org/art/collection/search/653217,1841,1841
10th–15th century,Tapestry Fragment,,33.149.52,http://www.metmuseum.org/art/collection/search/308087,900,1499
early 20th century (original dated 1480),Cup and Cover,,"09.200.16a, b",http://www.metmuseum.org/art/collection/search/463210,1480,1480
,Cupid with a Dog,Luigi Saulini,93.6.2,http://www.metmuseum.org/art/collection/search/187492,,
1760–75,Tea Spoon,Myer Myers,23.80.38,http://www.metmuseum.org/art/collection/search/8467,1760,1775
,Routledge's Every Girl's Annual,"Alice A. Leith|George Routledge & Sons, London|Kate Greenaway|Edmund Evans|Alfred Chantrey Corbould|Mary Ellen Edwards|Dalziel Brothers|William James Palmer|Francis Barraud",1983.1223.23,http://www.metmuseum.org/art/collection/search/353118,,
4th–7th century,Belt Buckle Attachment Plate,,X.209.28,http://www.metmuseum.org/art/collection/search/469788,400,699
,Mediceae familiae rerum feliciter gestarum victoriae et triumphi..,"Jan van der Straet, called Stradanus",49.95.1013-.1028,http://www.metmuseum.org/art/collection/search/357630,,
1539,Melancholia,Sebald Beham,62.635.33,http://www.metmuseum.org/art/collection/search/417967,1539,1539
1915–41,Necktie,,C.I.41.105.123,http://www.metmuseum.org/art/collection/search/84201,1915,1941
ca. 1864,"[Portal, Church of Saint-Trophime, Arles]",Edouard Baldus,1994.179.1,http://www.metmuseum.org/art/collection/search/267017,1864,1864
1720–1804,Design for a Cupola with Old and New Testament Figures,Pietro de Angelis|Domenico de Angelis,60.630.1,http://www.metmuseum.org/art/collection/search/341938,1720,1804
,"17th Plate, February 25th-28th, from Les Images De Tous Les Saincts et Saintes de L'Année (Images of All of the Saints and Religious Events of the Year), including  Images des Fêtes Mobiles (Images of Moveable Feasts from the Christian Calendar)",Jacques Callot|Israël Henriet,57.650.419(19),http://www.metmuseum.org/art/collection/search/422458,,
,Jug,,34.107.10,http://www.metmuseum.org/art/collection/search/322984,,
ca. 1875,Full-size patterns for facsimiles of front and back halves of foot of Bryant Vase,Tiffany & Co.,"1985.191.3e, f",http://www.metmuseum.org/art/collection/search/3859,1875,1875
,"Card Number 183, Mike LaCoss, Cincinnati Reds",Donruss,2016.402.598,http://www.metmuseum.org/art/collection/search/778429,,
1838,"Plate 32: What in the devil Macaire!, from 'Caricaturana,' published in Les Robert Macaires",Honoré Daumier|Aubert et Cie|Aubert et Cie|Charles Philipon,53.693.47,http://www.metmuseum.org/art/collection/search/759525,1838,1838
490–470 BCE,Terracotta fragment of a kylix (drinking cup),,2011.604.1.6718,http://www.metmuseum.org/art/collection/search/709882,-490,-470
```

If you'd like, I can also provide this as a downloadable file format, or write a short script (Python/pandas) that derives the same columns automatically from the Object Date text.