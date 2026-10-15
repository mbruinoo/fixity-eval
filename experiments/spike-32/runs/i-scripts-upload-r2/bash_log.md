## call 4

```
cd /mnt/user-data && python3 standardize_tsv.py
```

```
============================================================
ORIGINAL FILE ANALYSIS
============================================================
Columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Shape: (100, 4)
Missing values:
Object Date      5
Title            8
Object Number    0
Link Resource    0
dtype: int64


Traceback (most recent call last):
  File "/mnt/user-data/standardize_tsv.py", line 20, in <module>
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
         ^^^^^^^^^^^
  File "/usr/local/lib/python3.13/dist-packages/pandas/core/generic.py", line 6194, in __getattr__
    return object.__getattribute__(self, name)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
AttributeError: 'DataFrame' object has no attribute 'applymap'

```

## call 6

```
cd /mnt/user-data && python3 standardize_tsv.py
```

```
============================================================
ORIGINAL FILE ANALYSIS
============================================================
Columns: ['Object Date', 'Title', 'Object Number', 'Link Resource']
Shape: (100, 4)
Missing values:
Object Date      5
Title            8
Object Number    0
Link Resource    0
dtype: int64

============================================================
STANDARDIZATION COMPLETE
============================================================
Output file: /mnt/user-data/outputs/met_inventory_standardized.tsv
Total rows: 100
Total columns: 5

Columns: ['Row_ID', 'Object_Date', 'Title', 'Object_Number', 'Link_Resource']

Missing values by column:
Row_ID           0
Object_Date      5
Title            8
Object_Number    0
Link_Resource    0
dtype: int64

First 15 rows of standardized data:
    Row_ID                Object_Date                                                                                                                 Title    Object_Number                                          Link_Resource
0        1         ca. 1850–1640 B.C.                                                                                                          Hippopotamus         15.3.185  http://www.metmuseum.org/art/collection/search/546689
1        2         ca. 1479–1458 B.C.                                                                          Funerary Cone of Nakht and His Wife Senhotep         30.6.183  http://www.metmuseum.org/art/collection/search/554919
2        3         ca. 1479–1458 B.C.                                                                                                                 Arrow         36.3.225  http://www.metmuseum.org/art/collection/search/560249
3        4         ca. 1200–1194 B.C.                                                                           Inlay Representing the Cartouche of Seti II         67.161.2  http://www.metmuseum.org/art/collection/search/561165
4        5                664–30 B.C.                                                                                                                  Apis         04.2.486  http://www.metmuseum.org/art/collection/search/552470
5        6                500–480 BCE                                                                         Terracotta fragment of a kylix (drinking cup)  2011.604.1.4727  http://www.metmuseum.org/art/collection/search/698925
6        7            4th century BCE                                                                                                                   NaN   2002.201.82a–p   http://www.metmuseum.org/art/collection/search/59504
7        8       late 4th century BCE                                                                                  Marble head of a youth from a relief          11.91.1  http://www.metmuseum.org/art/collection/search/248476
8        9        ca. 4th–5th century                                                                                                                   NaN      1992.256.33   http://www.metmuseum.org/art/collection/search/51268
9       10                7th century                                                                                                                   Bag         32.32.11  http://www.metmuseum.org/art/collection/search/308024
10      11  probably 8th–12th century                                                                                                       Stucco Fragment      48.101.1611  http://www.metmuseum.org/art/collection/search/741109
11      12  probably 8th–12th century                                                                                                       Stucco Fragment       48.101.385  http://www.metmuseum.org/art/collection/search/740753
12      13  probably 8th–12th century                                                                                                       Stucco Fragment       48.101.705  http://www.metmuseum.org/art/collection/search/741770
13      14      probably 15th century                                                                                                   Page of Calligraphy       1979.137.1  http://www.metmuseum.org/art/collection/search/452933
14      15  early to mid-16th century  Palazzo dei Conservatori, coffered ceiling, ceiling plan and details; Sphinx, perspective view (recto) blank (verso)          49.92.2  http://www.metmuseum.org/art/collection/search/360453

```

