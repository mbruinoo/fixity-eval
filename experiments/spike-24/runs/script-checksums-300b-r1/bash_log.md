## call 2

```
mkdir -p /mnt/user-data/outputs
```

```
(no output, exit code 0)
```

## call 5

```
cd /mnt/user-data/outputs && ls -la
```

```
total 44
drwxr-xr-x 2 root root  4096 Oct 14 02:59 .
drwx------ 5 root root  4096 Oct 14 02:56 ..
-rw-r--r-- 1 root root 34514 Oct 14 02:59 met_inventory_standardized.tsv

```

## call 6

```
find /tmp -name "*met*" -o -name "*.tsv" 2>/dev/null | head -20
```

```
(no output, exit code 0)
```

## call 7

```
cat > /tmp/met_inventory_original.tsv << 'EOF'
Object Date	Title	Object Number	Link Resource
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
August 17, 1864	Andersonville Prison, Georgia, South-west View of the Stockade, Showing the Deadline. Thirty-three Thousand Prisoners in Bastile	2022.506	http://www.metmuseum.org/art/collection/search/888448
ca. 1560	Arm Defense for Left Arm	29.158.95	http://www.metmuseum.org/art/collection/search/22788
late 19th–early 20th century	Arm Ornament	1978.412.1561	http://www.metmuseum.org/art/collection/search/311992
ca. 1615–1868	Arrowhead (&lt;i&gt;Yanone&lt;/i&gt;)	36.25.2605	http://www.metmuseum.org/art/collection/search/23765
1857	Babbicombe, from the Beach	63.606.1.4	http://www.metmuseum.org/art/collection/search/270856
late 19th–early 20th century	Bark Belt	1979.206.1547	http://www.metmuseum.org/art/collection/search/313770
8th–13th century	Beads	48.101.90k	http://www.metmuseum.org/art/collection/search/856206
18th century or later	Beads, string	10.130.3267	http://www.metmuseum.org/art/collection/search/320982
ca. 8th–7th century BCE	Bell	1978.514.5	http://www.metmuseum.org/art/collection/search/326579
early 17th century, with later additions	Belt	2010.110.10	http://www.metmuseum.org/art/collection/search/236992
19th century	Blade for a Short Sword (Wakizashi)	36.25.1665a–c	http://www.metmuseum.org/art/collection/search/24342
first quarter 17th century	Border	50.179.1	http://www.metmuseum.org/art/collection/search/227510
4th–7th century	Bowl	25.10.20.293	http://www.metmuseum.org/art/collection/search/478839
ca. 1730–50	Box	1982.31	http://www.metmuseum.org/art/collection/search/206916
1820	Brother Joseph in the Alps	49.21.200	http://www.metmuseum.org/art/collection/search/368203
mid-20th century	Canoe Prow	1978.412.1128	http://www.metmuseum.org/art/collection/search/311569
mid-20th century	Canoe Prow	1978.412.1136	http://www.metmuseum.org/art/collection/search/311577
1977	Card Number 339, Adrian Devine, Atlanta Braves	2016.402.121	http://www.metmuseum.org/art/collection/search/719381
1981	Card Number 55, Mike Norris, Oakland A's	2016.402.8	http://www.metmuseum.org/art/collection/search/718470
before 16th century	Celt	1994.35.381	http://www.metmuseum.org/art/collection/search/317247
1930s	Chest	1983.24.5	http://www.metmuseum.org/art/collection/search/482695
18th century	Chest	18.45.1	http://www.metmuseum.org/art/collection/search/455261
1753	Chinese Chairs, in Chippendale Drawings, Vol. I	20.40.1(23)	http://www.metmuseum.org/art/collection/search/390499
1834	Coffeepot (part of a tea service)	69.162.2a, b	http://www.metmuseum.org/art/collection/search/209461
dated A.H. 37?/ 98 CE ?	Coin	39.40.127.178	http://www.metmuseum.org/art/collection/search/457250
8th century	Coin	39.40.127.502	http://www.metmuseum.org/art/collection/search/457572
ca. 1653	Colossal statue of the Appenino by Giambologna to left, represented as a giant crouching at the entrance of a grotto, ramps to either side, a pond below, various figures, dogs, and birds to right, from 'Views of the villa at Pratolino' (Vues de la villa de Pratolino)	2012.136.537.6	http://www.metmuseum.org/art/collection/search/411196
ca. 1780	Commode (one of a pair)	61.189.1	http://www.metmuseum.org/art/collection/search/202578
1940	Coney Island	1977.538	http://www.metmuseum.org/art/collection/search/261984
1785–1800	Creamer	27.85.5	http://www.metmuseum.org/art/collection/search/2708
19th–20th century	Currency Blade	1989.388	http://www.metmuseum.org/art/collection/search/316329
1936	Deportation	45.139	http://www.metmuseum.org/art/collection/search/488161
ca. 1830–70	Design for a Four-Wheel Chaise	58.638.383	http://www.metmuseum.org/art/collection/search/841635
ca. 1900	Design for a Haircomb with Stylized Exotic Flowers and a Rope	53.670.14	http://www.metmuseum.org/art/collection/search/739319
1652–1725	Design for an Epitaph	52.570.250	http://www.metmuseum.org/art/collection/search/346336
664–332 B.C.	Disk with Bes and Wedjat Eye	04.2.186	http://www.metmuseum.org/art/collection/search/555270
1961, printed later	Distributore di benzina in viale Regina Giovanna, Milano	2018.503.2	http://www.metmuseum.org/art/collection/search/771807
1883	Done Gone Busted!	52.632.58	http://www.metmuseum.org/art/collection/search/896078
late 13th–early 14th century	Double Capital	25.120.739	http://www.metmuseum.org/art/collection/search/470965
1960–79	Dress	1994.279.8	http://www.metmuseum.org/art/collection/search/80386
ca. 1968	Dress	2009.300.8245	http://www.metmuseum.org/art/collection/search/175263
19th century	Drum	89.4.1762	http://www.metmuseum.org/art/collection/search/502309
1855–59, printed 1876	Edmond De Goncourt	1992.5148.20	http://www.metmuseum.org/art/collection/search/266798
n.d.	Emaunel Felicité de Dufort de Duras, Duc de Duras	49.125.95	http://www.metmuseum.org/art/collection/search/363716
1859–1900	Embossed Plan of the City of New York	54.90.1238	http://www.metmuseum.org/art/collection/search/381237
late 17th or early 18th century	Embroidered cross from an Omophorion	17.120.107	http://www.metmuseum.org/art/collection/search/219959
ca. 1825–30	Empress Alexandra Feodorowna	2002.576.1	http://www.metmuseum.org/art/collection/search/211493
1972	Etching in Four Parts	2003.391a–d	http://www.metmuseum.org/art/collection/search/363425
1855–59	Eugène Pelletan	1991.1198	http://www.metmuseum.org/art/collection/search/266480
ca. 1960	Evening dress	1979.144	http://www.metmuseum.org/art/collection/search/83961
after 1887	Fashion	54.627.3	http://www.metmuseum.org/art/collection/search/368001
14th–early 16th century	Feathered Ornament	1994.35.89	http://www.metmuseum.org/art/collection/search/316914
1579	Feste nelle nozze de don Francesco Medici gran duca di Toscana; et della ... sig. Bianca Cappello, Florence, October 14, 1579	31.34	http://www.metmuseum.org/art/collection/search/341762
late 19th–early 20th century	Figure (Gra or Garra)	1978.412.851	http://www.metmuseum.org/art/collection/search/311321
1610	Fiore D'Ogni Virtu Per le Nobili Et Honeste Matrone, page 25 (recto)	37.1(25)	http://www.metmuseum.org/art/collection/search/661764
20th century (?)	Flounce	37.20.325	http://www.metmuseum.org/art/collection/search/226180
18th century	Folding table fork	93.13.48	http://www.metmuseum.org/art/collection/search/187606
14th century	Fragment	08.256.336	http://www.metmuseum.org/art/collection/search/445609
16th century	Fragment of a Bowl	40.170.632	http://www.metmuseum.org/art/collection/search/450293
12th century	Fragment of a Bowl	08.256.161	http://www.metmuseum.org/art/collection/search/445457
14th century	Fragment of Dish	13.190.249	http://www.metmuseum.org/art/collection/search/446516
1751	Frieze with a satyr holding a wine grape and playing with putti, from Frises pour les architraves, cornices, et autres ornements d'architecture, plate 3, in A Bound Collection of Print Series Including Cheminées et Lambris, Alcoves à la Romaine, Feuillages et autres ornemens..., etc.	18.62.4(50)	http://www.metmuseum.org/art/collection/search/435318
18th–19th century	Galloon	36.90.1555	http://www.metmuseum.org/art/collection/search/224643
19th century	Garden cloche	33.104.933	http://www.metmuseum.org/art/collection/search/756832
4th–early 5th century	Glass Fragments	08.268.50a-l	http://www.metmuseum.org/art/collection/search/477111
2nd–3rd century CE	Glass jar	74.51.237	http://www.metmuseum.org/art/collection/search/239822
1887	Glasscock, Shortstop, Indianapolis, from the Old Judge series (N172) for Gypsy Queen and Old Judge Cigarettes	63.350.214.172.541	http://www.metmuseum.org/art/collection/search/402042
probably 4th century BCE	Gold ring	20.129	http://www.metmuseum.org/art/collection/search/250924
1562	Grotesque Panel	32.130.117	http://www.metmuseum.org/art/collection/search/727072
1895	Harper's: November	1984.1202.84	http://www.metmuseum.org/art/collection/search/339513
ca. 1981–1640 B.C.	Head of a doll	09.180.2311	http://www.metmuseum.org/art/collection/search/556839
1869	Head of the Virgin looking up to the right, after Reni	28.22.58	http://www.metmuseum.org/art/collection/search/668083
18th–19th century	Helmet and Cuirass	36.25.32a–e	http://www.metmuseum.org/art/collection/search/32093
ca. 1615–1868	Helmet Crest (Maidate)	36.25.219a–c	http://www.metmuseum.org/art/collection/search/24109
ca. 1910–29	Horizontal Frieze with a Pattern of Decorative Fern Leaves on Background of Horizontal Stripes	64.503.33	http://www.metmuseum.org/art/collection/search/423928
August 17, 1864	How They Buried Them at Andersonville, Georgia	2022.509	http://www.metmuseum.org/art/collection/search/888451
1794	Hurdy-Gurdy	89.4.1055	http://www.metmuseum.org/art/collection/search/501642
1849	Il Teatro la Fenice in Venezia edificato dallÁrchitetto Antonio Selva nel 1792 e ricostruito in parte in 1836, dai Fratelli Tommaso e Giambattista Meduna	38.65.2	http://www.metmuseum.org/art/collection/search/353868
7th–5th century BCE	Incised bowl with fox motif	62.266.26	http://www.metmuseum.org/art/collection/search/308316
March 20, 1785	Interior Ornamented Wall with Doors and Fireplace, nos. 344–350, plate 52 from "Designs for Various Ornaments"	2018.839.36	http://www.metmuseum.org/art/collection/search/390267
1913	Ira Courtney, from for the World's Champion Athletes series (T230)	63.350.247.230.10	http://www.metmuseum.org/art/collection/search/695043
1892	Iris: Sweet Message, from the series Floral Beauties and Language of Flowers (N75) for Duke brand cigarettes	63.350.204.75.27	http://www.metmuseum.org/art/collection/search/423371
1992	Jacket	2019.74	http://www.metmuseum.org/art/collection/search/819945
1934	Jane Wyatt in "One More River" a Universal picture, from the "Movie Stars" series (T84), issued with Golden Grain Tobacco by Brown and Williamson Tobacco Company	63.350.244.84.50	http://www.metmuseum.org/art/collection/search/784428
ca. 1390–1352 B.C.	Jar Label	17.10.857	http://www.metmuseum.org/art/collection/search/563851
750–600 BCE	Juglet	74.51.945	http://www.metmuseum.org/art/collection/search/240534
ca. 1930	Kammergymnastiek	1995.580.4	http://www.metmuseum.org/art/collection/search/267303
1940	Koekuk, No. 22, collector card from the American Indian Series (D6), issued by the Kelley Baking Company to promote Kelley's Bread	63.350.307.6.17	http://www.metmuseum.org/art/collection/search/680119
ca. 1928, printed 1976	Konditor	1979.521.1	http://www.metmuseum.org/art/collection/search/262500
16th–19th century	Kris Sheath	36.25.1150	http://www.metmuseum.org/art/collection/search/660029
1880s	Lamaire from Actresses (N264) issued by P. Lorillard Company to promote Red Cross Long Cut Tobacco	Burdick 221, N264.81	http://www.metmuseum.org/art/collection/search/891563
1891	Landau #4150	23.112.2433	http://www.metmuseum.org/art/collection/search/732679
early 18th century	Lansquenets Talking with Market Women	07.282.8	http://www.metmuseum.org/art/collection/search/337923
early 18th century	Lappets	42.150.23	http://www.metmuseum.org/art/collection/search/226947
1857	Le Lundi, from Physionomies Parisiennes, Masques et Visages, plate 43	29.107.79(25)	http://www.metmuseum.org/art/collection/search/411099
July 6, 1853	Le mari s'assoupissant. Je suis sur que nous formons un groupe..., from Les Plaisirs de La Campagne, published in Le Charivari, July 6, 1853	36.12.171	http://www.metmuseum.org/art/collection/search/645939
1964	Legendy Krakowskie	66.718.11	http://www.metmuseum.org/art/collection/search/350946
ca. 1920–30	Leo Maloney from Western Stars or Scenes Exhibit Cards series (W412)	63.350.615.412.489	http://www.metmuseum.org/art/collection/search/778718
ca. 1888	Leslie Chester, from the Actors and Actresses series (N45, Type 1) for Virginia Brights Cigarettes	63.350.203.45.99	http://www.metmuseum.org/art/collection/search/411510
February 1865–75	Louis Revoil	2005.100.588.6	http://www.metmuseum.org/art/collection/search/294510
1928	Loungewear	1979.569.11a–d	http://www.metmuseum.org/art/collection/search/94500
1922	Mabel Normand, Sennet Star, from the "Movie Stars" series (T85), issued with Strollers Cigarettes by Tobacco Products Corporation	63.350.244.85-2.14	http://www.metmuseum.org/art/collection/search/784529
1910–29	Man with a Mask	29.100.929	http://www.metmuseum.org/art/collection/search/340845
1806	Medea Calls on the Gods' Aid, from Les Metamorphoses d'Ovide, Traduction nouvelle Avec le texte latin, suivie d'une analyse de l'explication des Fables, de notes géographiques, historiques, mythologiques et critiques, Par M.G.T. Villenave; ornée de gravures d'après les dessins de MM. LeBarbier, Monsiau et Moreau. A Paris, Chez les Éditeurs, F. Gay Libraire, rue de la Harpe, Bureau de la Bible; Ch. Guestard, Avocat, rue Saint Germain-l'Auxerrois. De l'Imprimerie de P. Didot l'aîné. MDCCCVI.	46.132.1(155)	http://www.metmuseum.org/art/collection/search/426187
1895	Memorial of 25th Anniversary of the Danish Brewery of Ny Carlsberg	04.22	http://www.metmuseum.org/art/collection/search/188922
1703/4	Miniature kettle with stand and brazier	63.53.110a–e	http://www.metmuseum.org/art/collection/search/202823
1857–72	Mirabeau Before the Convention	1978.420	http://www.metmuseum.org/art/collection/search/206751
1953	Montana Gold, from the "Frontier Days" series (R701-5), issued by Bowman Gum Company	63.350.329.701-5.6	http://www.metmuseum.org/art/collection/search/779418
ca. 1645–46	Musketeer Galloping Towards the Left	37.10.1(5)	http://www.metmuseum.org/art/collection/search/382529
ca. 1885	Natural History Buildings, Massachusetts Institute of Technology	2015.400.562	http://www.metmuseum.org/art/collection/search/698238
19th century	Nautilus cup	1974.28.209a, b	http://www.metmuseum.org/art/collection/search/205691
1907	Norfolk suit	1992.9.3a, b	http://www.metmuseum.org/art/collection/search/82458
1940	Nude, Portland, Oregon	1987.1100.498	http://www.metmuseum.org/art/collection/search/265573
1935–43	Old Farmhouse	43.33.459	http://www.metmuseum.org/art/collection/search/398109
1841	On fait des conts à l'actionnaire, from Les Lorettes, plate 7	20.57(7)	http://www.metmuseum.org/art/collection/search/410933
1935–43	On the Way to Coney Island	43.33.1030	http://www.metmuseum.org/art/collection/search/374932
7th century	Ostrakon	12.180.225	http://www.metmuseum.org/art/collection/search/474649
ca. 1641–78	Pack-horse, seated man with staff in right hand, and dog, all viewed from the rear, from the series 'The Small Landscapes'	2012.136.674	http://www.metmuseum.org/art/collection/search/399418
1973	Painting from a Ceremonial House Ceiling	1975.372.120	http://www.metmuseum.org/art/collection/search/310142
1768–69	Pair of candelabra	48.187.393a, b, .394a, b	http://www.metmuseum.org/art/collection/search/200358
ca. 1615–1868	Pair of Greaves (Sunē-atē)	36.25.445a, b	http://www.metmuseum.org/art/collection/search/24229
18th century	Pair of rosettes	07.225.510.664a, b	http://www.metmuseum.org/art/collection/search/190387
1858	Petit Journal pour rire, Volume 3, numbers 105–156	57.644.2(3)	http://www.metmuseum.org/art/collection/search/688735
[1862]	Phylloptera oblongifolia	19.16.4	http://www.metmuseum.org/art/collection/search/385440
19th century	Piece	36.90.2277	http://www.metmuseum.org/art/collection/search/225356
19th century	Piece	09.50.686	http://www.metmuseum.org/art/collection/search/215974
1700–1938	Pin	C.I.38.23.494	http://www.metmuseum.org/art/collection/search/105120
900–925	Plaque with Jesus' Entry into Jerusalem	17.190.50	http://www.metmuseum.org/art/collection/search/464464
1943	Plate 2: composition of hybrid human and animal forms, two figures lower right, from the 'Popol-Vuh'	44.69(2)	http://www.metmuseum.org/art/collection/search/747938
1799	Plate 45 from "Los Caprichos": There is Plenty to Suck (Mucho hay que chupar)	18.64(45)	http://www.metmuseum.org/art/collection/search/380460
June 20, 1790	Plate 6, Outlines of Figures, Landscapes and Cattle...for the Use of Learners	53.638.27(6)	http://www.metmuseum.org/art/collection/search/823250
1606	Plate 7: Hosea, from 'The Prophets'	55.565.4(8)	http://www.metmuseum.org/art/collection/search/648934
before 16th century	Pointed Stone Blade	1994.35.427	http://www.metmuseum.org/art/collection/search/317283
	Portrait of a Man	25.106.19	http://www.metmuseum.org/art/collection/search/436366
1632	Portrait of Claude Deruet and His Son, Jean	57.650.319	http://www.metmuseum.org/art/collection/search/422183
1878–93	Price List no. 46. Silver Plated Spoons, Forks, Knives, Etc....	58.623.1	http://www.metmuseum.org/art/collection/search/356373
1966	Proof for White Line Square series	1977.635.22	http://www.metmuseum.org/art/collection/search/426378
ca. 1621–22	Pulliciniello and Signora Lucretia, from Balli di Sfessania (Dance of Sfessania), plate 9	57.650.305(9)	http://www.metmuseum.org/art/collection/search/421495
1871	Queen Victoria	49.40.101	http://www.metmuseum.org/art/collection/search/770448
	Quiet Man	53.29	http://www.metmuseum.org/art/collection/search/488739
1889	Quoits, from the Games and Sports series (N165) for Old Judge Cigarettes	63.350.214.165.39	http://www.metmuseum.org/art/collection/search/400674
ca. 2100–2090 B.C.	Relief fragment possibly from the tomb of Mereri	98.4.76x	http://www.metmuseum.org/art/collection/search/590816
ca. 1981–1975 B.C.	Relief fragment, tomb of Meketre	20.3.581	http://www.metmuseum.org/art/collection/search/562493
ca. 2051–2030 B.C.	Relief from the tomb of Queen Neferu: a scribe and a cupbearer approach the queen's offering table	26.3.353f	http://www.metmuseum.org/art/collection/search/552053
	Reliquary with the Trinity	27.54.75	http://www.metmuseum.org/art/collection/search/625017
ca. 1740–94	René Descartes	49.116.48	http://www.metmuseum.org/art/collection/search/897061
1844	Reverend N.S. Wheaton, Rector of Christ Church, South Carolina	50.602.850	http://www.metmuseum.org/art/collection/search/785830
ca. 1352–1336 B.C.	Right foot of Akhenaten or Nefertiti prostrate	21.9.521	http://www.metmuseum.org/art/collection/search/549648
1780	Robert [i.e. Esek] Hopkins, Esq-r., Commdore of the American Sea Forces, from the "Hibernian Magazine"	24.90.787	http://www.metmuseum.org/art/collection/search/897179
1957	Ron Northey, Outfield, Chicago White Sox, from the "1957 Topps Regular Issue" series (R414-12), issued by Topps Chewing Gum Company.	68.757.31	http://www.metmuseum.org/art/collection/search/775719
first half 17th century	Rowel Spur	42.50.348	http://www.metmuseum.org/art/collection/search/29257
1928	Roy Stewart from Western Stars Exhibit Playing Cards (W403)	63.350.620.403.71	http://www.metmuseum.org/art/collection/search/767626
1607–56	Ruth and Boaz	1973.71	http://www.metmuseum.org/art/collection/search/338629
February 1968	S.M.S. No. 1, February, 1968	68.662.1	http://www.metmuseum.org/art/collection/search/353201
1644	Sacra Nemesis, the Levites Scourge	20.81.1.26	http://www.metmuseum.org/art/collection/search/360880
1925	Sample	43.42.39	http://www.metmuseum.org/art/collection/search/491099
1804	Sampler	57.122.763	http://www.metmuseum.org/art/collection/search/228679
19th century	Sampler	57.122.278	http://www.metmuseum.org/art/collection/search/228205
1723–26	Saucer (part of a service)	1974.356.431	http://www.metmuseum.org/art/collection/search/205981
ca. 1479–1425 B.C.	Scarab	10.130.124	http://www.metmuseum.org/art/collection/search/554577
1950s	Scarf	1982.401.19	http://www.metmuseum.org/art/collection/search/92411
1800–1820	Sconce	46.67.81a–c	http://www.metmuseum.org/art/collection/search/7348
ca. 2030–1640 B.C.	Sealing	14.3.310b	http://www.metmuseum.org/art/collection/search/565771
executed ca. 1930	Seated Youth (Le Realisateur)	53.140.7	http://www.metmuseum.org/art/collection/search/201584
ca. 1194–1188 B.C.	Shabti of Siptah	14.6.271	http://www.metmuseum.org/art/collection/search/559276
1910	Shaw, San Francisco, Pacific Coast League, from the "Obak Baseball Players" set (T212), issued by the American Tobacco Company to promote Obak Mouthpiece Cigarettes	63.350.246.212.155	http://www.metmuseum.org/art/collection/search/433727
mid-20th century	Shield	1978.412.929	http://www.metmuseum.org/art/collection/search/311390
18th century	Shield	02.5.2	http://www.metmuseum.org/art/collection/search/25041
1860–79	Shoes	C.I.38.76.4a, b	http://www.metmuseum.org/art/collection/search/90411
1970–79	Shoes	2009.300.8249a, b	http://www.metmuseum.org/art/collection/search/175267
19th century	Shouting Peasant	1974.28.144	http://www.metmuseum.org/art/collection/search/205647
1637	Sixth scene, the heavens, from 'The marriage of the gods' (Le nozze degli Dei)	2012.136.558.1	http://www.metmuseum.org/art/collection/search/412711
1890	Sketches of a Canoe and Sailboats (from Sketchbook)	1995.379.4v verso	http://www.metmuseum.org/art/collection/search/15781
late 18th century	Small cup (part of a set)	11.60.36	http://www.metmuseum.org/art/collection/search/191660
ca. 1750	Snuff spoon	36.156.5	http://www.metmuseum.org/art/collection/search/197818
1774–75	Souvenir	17.190.1319a–c	http://www.metmuseum.org/art/collection/search/193959
1967	SP XII	68.560.6	http://www.metmuseum.org/art/collection/search/373239
late 19th century	Standing cup	81.8.55	http://www.metmuseum.org/art/collection/search/186006
ca. 1st–2nd century	Statuette of Herakles holding apples	26.7.859	http://www.metmuseum.org/art/collection/search/571915
ca. 1888	Straight/ Mixed, from the Inaugural Types series (N237), issued by Kinney Bros.	Burdick 218, N237.1	http://www.metmuseum.org/art/collection/search/726592
probably 8th–12th century	Stucco Fragment	48.101.917	http://www.metmuseum.org/art/collection/search/741982
1879	Study for "The Almeh"	20.166.2	http://www.metmuseum.org/art/collection/search/333826
ca. 1951	Study for Judas Kiss: Christ and Judas	63.190.4	http://www.metmuseum.org/art/collection/search/489271
1930	Study of Objects	1991.402.12	http://www.metmuseum.org/art/collection/search/485817
ca. 1996	Suit	1999.56.2a, b	http://www.metmuseum.org/art/collection/search/81240
probably 18th–19th century	Swan-Neck Bottle (Ashkdan)	91.1.1558	http://www.metmuseum.org/art/collection/search/444736
19th century	Sword Guard (Tsuba)	36.120.27	http://www.metmuseum.org/art/collection/search/30038
1838/39	Teapot	2002.488	http://www.metmuseum.org/art/collection/search/211489
6th century BCE	Terracotta architectural tile	26.199.68	http://www.metmuseum.org/art/collection/search/252638
ca. 2650–2150 BCE	Terracotta collar-necked jar with two handles	27.120.11	http://www.metmuseum.org/art/collection/search/252909
460–440 BCE	Terracotta fragment of a column-krater (bowl for mixing wine and water)	2011.604.2.507	http://www.metmuseum.org/art/collection/search/729025
4th century BCE	Terracotta fragment of a krater (deep bowl)	2011.604.12.9	http://www.metmuseum.org/art/collection/search/768131
520–500 BCE	Terracotta fragment of a kylix (drinking cup)	2011.604.1.2830	http://www.metmuseum.org/art/collection/search/689385
490–480 BCE	Terracotta fragment of a kylix (drinking cup)	2011.604.1.8803	http://www.metmuseum.org/art/collection/search/759748
510–490 BCE	Terracotta fragment of a kylix (drinking cup)	2011.604.1.5367	http://www.metmuseum.org/art/collection/search/703481
second quarter of the 5th century BCE	Terracotta fragment of a kylix (drinking cup)	2011.604.1.8709	http://www.metmuseum.org/art/collection/search/728506
late 6th century BCE	Terracotta fragment of a plate?	2011.604.3.1042	http://www.metmuseum.org/art/collection/search/750299
first quarter of the 5th century BCE	Terracotta fragment of a trefoil olpe (jug)	2011.604.3.2736	http://www.metmuseum.org/art/collection/search/760019
last quarter of the 6th century BCE	Terracotta fragment of an oinochoe: chous (jug)?	2011.604.3.2762	http://www.metmuseum.org/art/collection/search/760013
490–470 BCE	Terracotta fragments of a kylix (drinking cup)	2011.604.1.6970a–d	http://www.metmuseum.org/art/collection/search/713515
3rd century BCE (?)	Terracotta male head wearing a wreath	74.51.1505	http://www.metmuseum.org/art/collection/search/241061
mid-5th century BCE	Terracotta rim fragment of a kylix (drinking cup)	2011.604.1.4241	http://www.metmuseum.org/art/collection/search/695812
first half of the 5th century BCE	Terracotta rim fragment of a kylix (drinking cup)	2011.604.1.1955	http://www.metmuseum.org/art/collection/search/683752
3rd–4th century	Textile Fragment	89.18.51	http://www.metmuseum.org/art/collection/search/443256
ca. 1900	Textile sample	08.21.490	http://www.metmuseum.org/art/collection/search/480280
1895 or before	The Bath	29.100.186	http://www.metmuseum.org/art/collection/search/336789
	The Beautiful Virgin of Regensburg in a Church	17.42.10	http://www.metmuseum.org/art/collection/search/429695
2019	The Broken Five	2021.56a, b	http://www.metmuseum.org/art/collection/search/845852
1895	The Chap-Book: May	1984.1202.9	http://www.metmuseum.org/art/collection/search/339049
1889	The Cliffs of Aberdeenshire	17.3.2126	http://www.metmuseum.org/art/collection/search/706287
August 1, 1870	The competition at the conservatory: At the 79th audition of "Oh, what a pleasure to be a soldier!", from 'News of the day,' published in "Le Charivari"	22.61.24	http://www.metmuseum.org/art/collection/search/757127
ca. 1863	The Delaware Valley	99.27	http://www.metmuseum.org/art/collection/search/11228
1876–1918	The Dream (La Rêve)	68.540.8	http://www.metmuseum.org/art/collection/search/819432
ca. 1835	The Gentleman's Valentine Writer	1981.1136.30	http://www.metmuseum.org/art/collection/search/353684
ca. 1427–1400 B.C.	The Goddess Renenutet, Tomb of Qenamun	30.4.171	http://www.metmuseum.org/art/collection/search/557720
1932	The Graveyard by the Sea	66.656.3	http://www.metmuseum.org/art/collection/search/349388
January 1st, 1874	The Household Companion Illustrating White Wire Goods	62.653.3	http://www.metmuseum.org/art/collection/search/349999
1914	The Musician's Table	2018.216	http://www.metmuseum.org/art/collection/search/788081
ca. 1750–78	The Pyramid of Gaius Cestius, from "Vedute di Roma" (Roman Views), part II	41.71.1.17(7)	http://www.metmuseum.org/art/collection/search/409348
1958	The Tapistry (La tapisserie)	1985.1137.61	http://www.metmuseum.org/art/collection/search/687617
1850	The Tarantella Dance	44.91.826	http://www.metmuseum.org/art/collection/search/430556
1805	The Turnpike Gate	41.105.38	http://www.metmuseum.org/art/collection/search/680677
published 1703 or 1712	Title Plate with a Vase on a Pedestal, from Vasses de la Maison Royalle de L'oo, part of Œuvres du Sr. D. Marot	30.4(94)	http://www.metmuseum.org/art/collection/search/427330
1840	Titus Bastianilli	50.602.828	http://www.metmuseum.org/art/collection/search/652956
15th–16th century	Torch Holder	55.61.59	http://www.metmuseum.org/art/collection/search/471625
1864	Traité Pratique de Construction Navale	2016.708.9	http://www.metmuseum.org/art/collection/search/742618
1993, printed 1996	Transfiguration #10008	1997.333.3	http://www.metmuseum.org/art/collection/search/281987
before 1789	Trophies. The Arts, etc.	54.603.2(9-13)	http://www.metmuseum.org/art/collection/search/355311
published 1657	Two designs with a bust of the Virgin at upper left in a medallion, from Frises ou montants à la moderne, plate 5, bound in Oeuvres. Vol. IV	33.84(4.174)	http://www.metmuseum.org/art/collection/search/433423
1823	Two Men before a Waterfall at Sunset	2019.167.3	http://www.metmuseum.org/art/collection/search/439344
1901 or 1902	Two Women	1997.391.3	http://www.metmuseum.org/art/collection/search/438001
1912	Tyrol: Bridge over the Inn River, Brixlegg (Innbrücke, Brixlegg, Tirol)	WW.636	http://www.metmuseum.org/art/collection/search/650265
1983	Untitled	2019.20.2	http://www.metmuseum.org/art/collection/search/818222
1937	Untitled, from "American Abstract Artists Portfolio"	1978.558.3(7)	http://www.metmuseum.org/art/collection/search/431984
ca. 1981–1640 B.C.	Vase fragment	X.632.7	http://www.metmuseum.org/art/collection/search/560587
1970	Venus Garden	1985.81a-l	http://www.metmuseum.org/art/collection/search/484378
1644	Venus, from 'Game of Mythology' (Jeu de la Mythologie)	2012.136.811.12	http://www.metmuseum.org/art/collection/search/412356
1802	View of the Gate of St. Denis, taken from the Suburbs	24.46.10	http://www.metmuseum.org/art/collection/search/821817
ca. 1641	Virgin and Christ Child	17.50.17-297	http://www.metmuseum.org/art/collection/search/373773
1933	Volume 3: progressive proofs for plates 17-24 for Charlot's 'Picture Book'	34.80(3)	http://www.metmuseum.org/art/collection/search/713159
1760–70	Waistcoat	2009.300.2855	http://www.metmuseum.org/art/collection/search/157726
1855–65	Walking boots	2009.300.5484a, b	http://www.metmuseum.org/art/collection/search/169699
17th–18th century	Watch cock	13.173.123	http://www.metmuseum.org/art/collection/search/192463
third quarter 17th century	Wedding knife, fork and sheath	64.101.1595–.1597	http://www.metmuseum.org/art/collection/search/210073
early 20th century	White Bearded Gnu, collector card from the Animals series (D9), issued by the Weber Baking Company to promote Onist Milk and Pullman Bread	63.350.307.9.29	http://www.metmuseum.org/art/collection/search/680219
17th century	Window	93.26.14	http://www.metmuseum.org/art/collection/search/453572
ca. 1929	Yakima Canutt in Arrow Pictures from Western Stars or Scenes Exhibit Cards series (W412)	63.350.613.412.149	http://www.metmuseum.org/art/collection/search/773052
5th century BCE	东周 玉璜|Arc-shaped pendant (Huang)	2009.92	http://www.metmuseum.org/art/collection/search/75285
20th century	擦條|Sand-file for carving jade	1981.296.18	http://www.metmuseum.org/art/collection/search/62070
datable to 1506–10	明　文徵明　致丈人吳愈書　冊頁|Letter to the artist's father-in-law, Wu Yu	1989.363.59	http://www.metmuseum.org/art/collection/search/45775
1950s	棟方志功筆　蒼赫二童子図|Red and Blue, Two Attendants	2018.853.35	http://www.metmuseum.org/art/collection/search/816263
19th century	清 緙絲乾隆南巡宮苑圖|Scenic Sites in the Qianlong Emperor's Southern Inspection Tour	13.220.134	http://www.metmuseum.org/art/collection/search/68288
1838	蝉小川|The Cicada Stream (Semi no Ogawa)  蝉小川	2013.787a–c	http://www.metmuseum.org/art/collection/search/78689
1840	蹄斎北馬筆　五美人図|Five Beauties	2015.500.9.12	http://www.metmuseum.org/art/collection/search/667347
dated 1978	近代  應野平  破墨山水  扇面|Broken-ink Landscape	1986.267.410	http://www.metmuseum.org/art/collection/search/36399
dated 1978	近代  程十髮  雜畫  冊頁十四開|Various Subjects	1986.267.435a–p	http://www.metmuseum.org/art/collection/search/36421
EOF
md5sum /tmp/met_inventory_original.tsv
```

```
b78813c842842bd25fbd61d1cae0a1b4  /tmp/met_inventory_original.tsv

```

## call 9

```
cp /tmp/met_inventory_original.tsv /mnt/user-data/outputs/met_inventory_original.tsv
```

```
(no output, exit code 0)
```

## call 10

```
cd /mnt/user-data/outputs && python3 transform_met_inventory.py
```

```
Input file checksum (MD5): b78813c842842bd25fbd61d1cae0a1b4
Input file: /tmp/met_inventory_original.tsv
Processing 301 lines...
Output file checksum (MD5): 47fd11c60ad238d33c4dc1a3d12ff104
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv

============================================================
TRANSFORMATION REPORT
============================================================
Total lines processed: 301
Lines with transformations: 106
En-dashes replaced: 88
Quotation marks removed: 1
Bracket delimiters removed: 9
HTML tags removed: 1
============================================================

Summary written to: /mnt/user-data/outputs/transformation_summary.txt

```

## call 11

```
cd /mnt/user-data/outputs && echo "=== VERIFICATION ===" && echo "" && echo "Original file:" && md5sum met_inventory_original.tsv && echo "" && echo "Standardized file:" && md5sum met_inventory_standardized.tsv && echo "" && echo "Script file:" && md5sum transform_met_inventory.py
```

```
=== VERIFICATION ===

Original file:
b78813c842842bd25fbd61d1cae0a1b4  met_inventory_original.tsv

Standardized file:
47fd11c60ad238d33c4dc1a3d12ff104  met_inventory_standardized.tsv

Script file:
98db0494567c0348a6196ed58c00b953  transform_met_inventory.py

```

