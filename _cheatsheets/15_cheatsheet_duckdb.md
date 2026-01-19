## Aide-mémoire DuckDB

DuckDB est un SGBD SQL embarqué, orienté colonnes (OLAP), optimisé pour l'analyse. Intégration Python/pandas sans serveur.

---

### Connexion

```python
import duckdb

conn = duckdb.connect()                    # Mode mémoire (temporaire)
conn = duckdb.connect('ma_base.db')        # Mode persistant (fichier)
conn = duckdb.connect('base.db', read_only=True)  # Lecture seule
conn.close()                                # Fermer
```

---

### DDL (Définition de données)

```sql
-- Tables
CREATE TABLE produits (id INTEGER, nom VARCHAR, prix DECIMAL(10,2));
CREATE TABLE IF NOT EXISTS produits (id INTEGER, nom VARCHAR);
CREATE OR REPLACE TABLE produits (id INTEGER, nom VARCHAR);  -- Idempotent
CREATE TABLE produits_actifs AS SELECT * FROM produits WHERE stock > 0;

DROP TABLE produits;
DROP TABLE IF EXISTS produits;

-- Modification
ALTER TABLE produits ADD COLUMN categorie VARCHAR;
ALTER TABLE produits DROP COLUMN categorie;
ALTER TABLE produits RENAME COLUMN nom TO nom_produit;
```

---

### DML (Manipulation de données)

```sql
-- Sélection
SELECT nom, prix FROM produits;
SELECT * FROM produits WHERE prix > 100 AND stock > 0;
SELECT DISTINCT categorie FROM produits;
SELECT * FROM produits WHERE nom LIKE '%vin%';
SELECT * FROM produits WHERE id IN (1, 2, 3);
SELECT * FROM produits WHERE prix BETWEEN 10 AND 50;
SELECT * FROM produits ORDER BY prix DESC;
SELECT * FROM produits LIMIT 10 OFFSET 20;

-- Insertion
INSERT INTO produits (id, nom, prix) VALUES (1, 'Vin Rouge', 25.50);

-- Mise à jour
UPDATE produits SET prix = 30.00 WHERE id = 1;

-- Suppression
DELETE FROM produits WHERE stock = 0;
```

---

### Jointures

```sql
SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.id;
SELECT * FROM table1 LEFT JOIN table2 ON table1.id = table2.id;
SELECT * FROM table1 RIGHT JOIN table2 ON table1.id = table2.id;
SELECT * FROM table1 FULL OUTER JOIN table2 ON table1.id = table2.id;
```

---

### Agrégations

```sql
SELECT COUNT(*), COUNT(DISTINCT categorie) FROM produits;
SELECT SUM(prix * stock), AVG(prix), MIN(prix), MAX(prix) FROM produits;
SELECT categorie, COUNT(*) FROM produits GROUP BY categorie;
SELECT categorie, AVG(prix) FROM produits GROUP BY categorie HAVING AVG(prix) > 20;
```

---

### Intégration Python

```python
import pandas as pd
import duckdb

# Exécution SQL
conn = duckdb.connect('ma_base.db')
conn.execute("CREATE TABLE produits (id INTEGER, nom VARCHAR)")
resultat = conn.execute("SELECT * FROM produits").fetchall()
df = conn.execute("SELECT * FROM produits").df()
conn.close()

# Pandas → DuckDB
df = pd.read_excel('fichier.xlsx')
conn = duckdb.connect('ma_base.db')
conn.register('df_temp', df)
conn.execute("CREATE OR REPLACE TABLE produits AS SELECT * FROM df_temp")
conn.close()

# DuckDB → Pandas
conn = duckdb.connect('ma_base.db')
df = conn.execute("SELECT * FROM produits").df()
conn.close()

# Requête directe sur DataFrame
df = pd.read_excel('fichier.xlsx')
resultat = duckdb.query("SELECT * FROM df WHERE prix > 20").df()
```

**Pattern nettoyage complet :**
```python
from pathlib import Path
import pandas as pd
import duckdb

path_source = Path(__file__).parent.parent / "sources" / "fichier.xlsx"
path_db = Path(__file__).parent.parent / "_bdd" / "ma_base.db"

df = pd.read_excel(path_source)
df_clean = df.dropna().drop_duplicates()

conn = duckdb.connect(database=str(path_db))
conn.register('df_clean', df_clean)
conn.execute("CREATE OR REPLACE TABLE table_clean AS SELECT * FROM df_clean")
nb_lignes = conn.execute("SELECT COUNT(*) FROM table_clean").fetchone()[0]
conn.close()
```

---

### Import/Export

```sql
-- Import
CREATE TABLE produits AS SELECT * FROM read_csv('fichier.csv');
CREATE TABLE produits AS SELECT * FROM read_csv('fichier.csv', delim=';', header=true);
CREATE TABLE produits AS SELECT * FROM read_parquet('fichier.parquet');
CREATE TABLE produits AS SELECT * FROM read_json('fichier.json');

-- Export
COPY produits TO 'export.csv' (HEADER, DELIMITER ',');
COPY produits TO 'export.parquet' (FORMAT PARQUET);
```

```python
# Export Python
conn = duckdb.connect('ma_base.db')
df = conn.execute("SELECT * FROM produits").df()
df.to_csv('export.csv', index=False)
df.to_excel('export.xlsx', index=False)
conn.close()
```

---

### Fonctions utiles

**Chaînes :** `CONCAT('A','B')`, `UPPER('hello')`, `LOWER('HELLO')`, `TRIM('  texte  ')`, `LENGTH('hello')`, `SUBSTRING('hello', 1, 3)`, `REPLACE('hello', 'l', 'r')`

**Dates :** `CURRENT_DATE`, `CURRENT_TIMESTAMP`, `DATE_TRUNC('month', date_col)`, `DATE_DIFF('day', date1, date2)`, `EXTRACT(YEAR FROM date_col)`

**Window :** 
```sql
SELECT sku, ROW_NUMBER() OVER (ORDER BY prix DESC) FROM produits;
SELECT categorie, RANK() OVER (PARTITION BY categorie ORDER BY prix DESC) FROM produits;
SELECT date, LAG(ventes, 1) OVER (ORDER BY date) FROM ventes;
```

**NULL :** `WHERE stock IS NULL`, `COALESCE(stock, 0)`, `NULLIF(stock, 0)`

**Statistiques :** `AVG()`, `STDDEV()`, `MEDIAN()`, `PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY prix)`

**Z-Score :** `(prix - AVG(prix) OVER ()) / STDDEV(prix) OVER ()`

**CTE :** 
```sql
WITH produits_chers AS (SELECT * FROM produits WHERE prix > 50)
SELECT * FROM produits_chers;
```

---

### Inspection

```sql
SHOW TABLES;
DESCRIBE produits;
PRAGMA table_info('produits');
EXPLAIN SELECT * FROM produits WHERE prix > 50;
```

---

### Bonnes pratiques

1. `CREATE OR REPLACE TABLE` pour idempotence
2. Toujours `conn.close()`
3. `Path()` pour chemins cross-platform
4. Pandas pour Excel, DuckDB pour CSV/Parquet
5. `conn.register()` pour pandas → DuckDB
6. Mode persistant pour conserver les données

**Ressources :** https://duckdb.org/docs/
