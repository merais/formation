# Conception du Data Lineage - P10 Orchestration des flux

---

## 1. IDENTIFICATION DES TÂCHES DE TRANSFORMATION

### 1.1 Vue d'ensemble du pipeline

```
[erp.xlsx]     ──┐
                 ├──> Nettoyage ──> Jointure ──> Agrégation ──> Classification ──> Extractions
[liaison.xlsx]  ─┤                                                                    ├──> rapport_ca.xlsx
[web.xlsx]   ────┘                                                                    ├──> vins_premium.csv
                                                                                      └──> vins_ordinaires.csv
```

---

## 2. LISTE DES TÂCHES DE NETTOYAGE

### 2.1 Nettoyage fichier ERP (erp.xlsx)
**Tâche 1 : Chargement ERP**
- Input : `erp.xlsx`
- Action : Charger le fichier dans DuckDB
- Tool : DuckDB
- Output : Table temporaire `erp_raw`

**Tâche 2 : Suppression valeurs manquantes ERP**
- Input : `erp_raw`
- Action : `DELETE FROM erp_raw WHERE colonne IS NULL`
- Tool : SQL DuckDB
- Output : `erp_no_null`

**Tâche 3 : Dédoublonnage ERP**
- Input : `erp_no_null`
- Action : `SELECT DISTINCT * FROM erp_no_null`
- Tool : SQL DuckDB
- Output : `erp_clean` (825 lignes attendues)

**Test 1 : Vérification nettoyage ERP**
- Vérifier : COUNT(*) = 825
- Vérifier : Aucune valeur NULL
- Vérifier : Aucun doublon sur clé primaire

---

### 2.2 Nettoyage fichier LIAISON (liaison.xlsx)
**Tâche 4 : Chargement LIAISON**
- Input : `liaison.xlsx`
- Action : Charger le fichier dans DuckDB
- Tool : DuckDB
- Output : Table temporaire `liaison_raw`

**Tâche 5 : Suppression valeurs manquantes LIAISON**
- Input : `liaison_raw`
- Action : `DELETE FROM liaison_raw WHERE colonne IS NULL`
- Tool : SQL DuckDB
- Output : `liaison_no_null`

**Tâche 6 : Dédoublonnage LIAISON**
- Input : `liaison_no_null`
- Action : `SELECT DISTINCT * FROM liaison_no_null`
- Tool : SQL DuckDB
- Output : `liaison_clean` (825 lignes attendues)

**Test 2 : Vérification nettoyage LIAISON**
- Vérifier : COUNT(*) = 825
- Vérifier : Aucune valeur NULL
- Vérifier : Aucun doublon sur clé primaire

---

### 2.3 Nettoyage fichier WEB (web.xlsx)
**Tâche 7 : Chargement WEB**
- Input : `web.xlsx`
- Action : Charger le fichier dans DuckDB
- Tool : DuckDB
- Output : Table temporaire `web_raw`

**Tâche 8 : Suppression valeurs manquantes WEB**
- Input : `web_raw`
- Action : `DELETE FROM web_raw WHERE colonne IS NULL`
- Tool : SQL DuckDB
- Output : `web_no_null` (1428 lignes attendues)

**Test 3 : Vérification nettoyage WEB (valeurs manquantes)**
- Vérifier : COUNT(*) = 1428
- Vérifier : Aucune valeur NULL

**Tâche 9 : Dédoublonnage WEB**
- Input : `web_no_null`
- Action : `SELECT DISTINCT * FROM web_no_null`
- Tool : SQL DuckDB
- Output : `web_clean` (714 lignes attendues)

**Test 4 : Vérification dédoublonnage WEB**
- Vérifier : COUNT(*) = 714
- Vérifier : Aucun doublon sur clé primaire

---

## 3. LISTE DES TÂCHES DE FUSION (JOINTURES)

### 3.1 Jointure ERP - LIAISON
**Tâche 10 : Jointure ERP-LIAISON**
- Input : `erp_clean` + `liaison_clean`
- Action : 
```sql
SELECT e.*, l.id_web
FROM erp_clean e
INNER JOIN liaison_clean l ON e.id_produit = l.id_erp
```
- Tool : SQL DuckDB
- Output : `erp_liaison_merged` (825 lignes attendues)

**Test 5 : Vérification cohérence jointure ERP-LIAISON**
- Vérifier : COUNT(*) = 825
- Vérifier : Aucune ligne avec id_web NULL
- Vérifier : Toutes les lignes de erp_clean sont présentes

---

### 3.2 Jointure avec WEB
**Tâche 11 : Jointure finale avec WEB**
- Input : `erp_liaison_merged` + `web_clean`
- Action : 
```sql
SELECT el.*, w.prix, w.quantite
FROM erp_liaison_merged el
INNER JOIN web_clean w ON el.id_web = w.id_produit_web
```
- Tool : SQL DuckDB
- Output : `donnees_fusionnees` (714 lignes attendues)

**Test 6 : Vérification cohérence jointure finale**
- Vérifier : COUNT(*) = 714
- Vérifier : Toutes les colonnes nécessaires présentes
- Vérifier : Pas de valeurs NULL sur colonnes critiques

---

## 4. LISTE DES TÂCHES D'AGRÉGATION

### 4.1 Calcul du chiffre d'affaires par produit
**Tâche 12 : Calcul CA par produit**
- Input : `donnees_fusionnees`
- Action : 
```sql
SELECT 
    id_produit,
    nom_produit,
    prix * quantite AS chiffre_affaires
FROM donnees_fusionnees
```
- Tool : SQL DuckDB
- Output : `ca_par_produit`

**Test 7 : Vérification CA par produit**
- Vérifier : Toutes les lignes ont un CA calculé
- Vérifier : CA >= 0 pour tous les produits

---

### 4.2 Calcul du chiffre d'affaires total
**Tâche 13 : Calcul CA total**
- Input : `ca_par_produit`
- Action : 
```sql
SELECT SUM(chiffre_affaires) AS ca_total
FROM ca_par_produit
```
- Tool : SQL DuckDB
- Output : `ca_total` (70 568,60 € attendu)

**Test 8 : Vérification CA total**
- Vérifier : ca_total = 70568.60

---

## 5. TÂCHES DE CLASSIFICATION (Z-SCORE)

### 5.1 Calcul du z-score
**Tâche 14 : Calcul statistiques des prix**
- Input : `donnees_fusionnees`
- Action : Calculer moyenne et écart-type des prix
```python
mean_price = df['prix'].mean()
std_price = df['prix'].std()
```
- Tool : Python (pandas)
- Output : Variables `mean_price`, `std_price`

**Tâche 15 : Calcul z-score par vin**
- Input : `donnees_fusionnees` + statistiques
- Action : 
```python
df['z_score'] = (df['prix'] - mean_price) / std_price
```
- Tool : Python (pandas)
- Output : Colonne `z_score` ajoutée

**Test 9 : Vérification validité z-score**
- Vérifier : Formule z-score correcte
- Vérifier : Pas de valeurs NaN ou Inf

---

### 5.2 Classification premium / ordinaire
**Tâche 16 : Classification des vins**
- Input : Données avec z-score
- Action : 
```python
df['categorie'] = df['z_score'].apply(lambda x: 'premium' if x > 2 else 'ordinaire')
```
- Tool : Python (pandas)
- Output : Colonne `categorie` ajoutée

**Test 10 : Vérification nombre vins premium**
- Vérifier : COUNT(WHERE categorie='premium') = 30

---

## 6. LISTE DES TÂCHES D'EXTRACTION

### 6.1 Extraction rapport CA (branche 1)
**Tâche 17 : Extraction rapport CA Excel**
- Input : `ca_par_produit` + `ca_total`
- Action : 
```python
with pd.ExcelWriter('rapport_ca.xlsx') as writer:
    ca_par_produit.to_excel(writer, sheet_name='CA par produit')
    ca_total.to_excel(writer, sheet_name='CA total')
```
- Tool : Python (pandas + openpyxl)
- Output : `rapport_ca.xlsx` (2 feuilles)

---

### 6.2 Extraction vins premium (branche 2)
**Tâche 18 : Filtrage vins premium**
- Input : Données classifiées
- Action : 
```python
vins_premium = df[df['categorie'] == 'premium']
```
- Tool : Python (pandas)
- Output : DataFrame `vins_premium`

**Tâche 19 : Extraction CSV vins premium**
- Input : `vins_premium`
- Action : 
```python
vins_premium.to_csv('vins_premium.csv', index=False)
```
- Tool : Python (pandas)
- Output : `vins_premium.csv`

---

### 6.3 Extraction vins ordinaires (branche 3)
**Tâche 20 : Filtrage vins ordinaires**
- Input : Données classifiées
- Action : 
```python
vins_ordinaires = df[df['categorie'] == 'ordinaire']
```
- Tool : Python (pandas)
- Output : DataFrame `vins_ordinaires`

**Tâche 21 : Extraction CSV vins ordinaires**
- Input : `vins_ordinaires`
- Action : 
```python
vins_ordinaires.to_csv('vins_ordinaires.csv', index=False)
```
- Tool : Python (pandas)
- Output : `vins_ordinaires.csv`

---

## 7. RÉSUMÉ DES POINTS DE TEST

| Test ID | Point de test | Valeur attendue | Type |
|---------|---------------|-----------------|------|
| Test 1 | Lignes après nettoyage ERP | 825 | SQL COUNT |
| Test 2 | Lignes après nettoyage LIAISON | 825 | SQL COUNT |
| Test 3 | Lignes après suppression NULL WEB | 1428 | SQL COUNT |
| Test 4 | Lignes après dédoublonnage WEB | 714 | SQL COUNT |
| Test 5 | Lignes après jointure ERP-LIAISON | 825 | SQL COUNT |
| Test 6 | Lignes après jointure finale | 714 | SQL COUNT |
| Test 7 | CA positifs | Tous >= 0 | SQL WHERE |
| Test 8 | CA total | 70 568,60 € | SQL SUM |
| Test 9 | Z-score valides | Pas de NaN/Inf | Python assert |
| Test 10 | Nombre vins premium | 30 | Python COUNT |

---