## call 1

```
cd /mnt/user-data/outputs && head -50 <<'EOF'
Object Date	Title	Object Number	Link Resource
EOF

```

```
Object Date	Title	Object Number	Link Resource

```

## call 4

```
cd /mnt/user-data && find . -name "*.tsv" -o -name "*inventory*" | head -20
```

```
./outputs/met_inventory_standardized.tsv
./uploads/met_inventory.tsv

```

## call 5

```
cd /mnt/user-data && sha256sum uploads/met_inventory.tsv && md5sum uploads/met_inventory.tsv
```

```
33c53888daa063ca9697f4a82f15cd2d047afbce1ccb21c235e9c4ae9509d547  uploads/met_inventory.tsv
6ec5bfc2d979ad12eb3343149beb8617  uploads/met_inventory.tsv

```

