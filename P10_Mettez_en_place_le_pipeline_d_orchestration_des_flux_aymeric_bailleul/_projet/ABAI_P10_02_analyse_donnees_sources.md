# Analyse des données sources - P10

## 1. FICHIER ERP (Fichier_erp.xlsx)

### Structure
- **Nombre de lignes** : 825
- **Nombre de colonnes** : 5

### Colonnes
| Nom colonne | Type | Description |
|-------------|------|-------------|
| product_id | int64 | Identifiant produit (clé primaire potentielle) |
| onsale_web | int64 | Indicateur de vente en ligne (0 ou 1) |
| price | float64 | Prix du produit |
| stock_quantity | int64 | Quantité en stock |
| stock_status | object | Statut du stock (outofstock, instock) |

### Qualité des données
- **Valeurs manquantes** : Aucune
- **Doublons complets** : 0
- **Clé primaire identifiée** : `product_id` (825 valeurs uniques, pas de doublons)

### Observations
- Les colonnes onsale_web et stock_status ont seulement 2 valeurs uniques chacune
- Fichier propre, pas de valeurs manquantes
- product_id est unique et peut servir de clé primaire

---

## 2. FICHIER LIAISON (fichier_liaison.xlsx)

### Structure
- **Nombre de lignes** : 825
- **Nombre de colonnes** : 2

### Colonnes
| Nom colonne | Type | Description |
|-------------|------|-------------|
| product_id | int64 | Identifiant produit (lié à ERP) |
| id_web | object | Identifiant web (lié à WEB via sku) |

### Qualité des données
- **Valeurs manquantes** : 91 sur id_web (11.03%)
- **Doublons complets** : 0
- **Doublons sur id_web** : 90 (734 valeurs uniques sur 825 lignes)

### Observations
- Ce fichier fait le lien entre le système ERP et le CMS Web
- 11% de valeurs manquantes sur id_web à gérer
- Les doublons sur id_web suggèrent qu'un même produit web peut avoir plusieurs références ERP
- **IMPORTANT** : Les valeurs NULL sur id_web doivent être CONSERVEES pour obtenir 825 lignes

---

## 3. FICHIER WEB (Fichier_web.xlsx)

### Structure
- **Nombre de lignes** : 1513
- **Nombre de colonnes** : 28

### Colonnes principales
| Nom colonne | Type | Description |
|-------------|------|-------------|
| sku | object | Identifiant unique produit (clé primaire potentielle) |
| virtual | int64 | Indicateur produit virtuel |
| downloadable | int64 | Indicateur téléchargeable |
| rating_count | int64 | Nombre d'évaluations |
| average_rating | float64 | Note moyenne |
| total_sales | float64 | Total des ventes |
| tax_status | object | Statut taxe |
| post_title | object | Titre du produit |
| post_type | object | Type de publication (product, attachment) |
| post_date | datetime64 | Date de publication |

### Qualité des données
- **Valeurs manquantes importantes** :
  - tax_class, post_content, post_password, post_content_filtered : 100%
  - tax_status, post_excerpt, post_mime_type : ~53%
  - Autres colonnes : ~5.5%
- **Doublons complets** : 82
- **Doublons sur sku** : 798 (714 valeurs uniques sur 1513 lignes)

### Observations
- Le fichier contient des données de CMS WordPress (colonnes post_*)
- Beaucoup de colonnes avec 100% de valeurs manquantes (à supprimer)
- Le champ `sku` semble être la clé primaire mais contient :
  - 5.6% de valeurs manquantes (85 lignes)
  - 798 doublons (714 valeurs uniques)
- Le fichier contient différents types de contenu (post_type) : products et attachments
- **VALIDATION** : Filtrer post_type='product' + supprimer NULL sku + dédoublonner = 714 lignes directement

---

## 4. RELATIONS ENTRE LES FICHIERS

### Schéma de liaison
```
ERP (product_id) <---> LIAISON (product_id, id_web) <---> WEB (sku)
```

### Détails des relations
1. **ERP ↔ LIAISON** : Relation via `product_id`
   - Colonne commune : `product_id`
   - Type de relation : 1:1 (825 lignes dans chaque fichier)

2. **LIAISON ↔ WEB** : Relation via id_web (LIAISON) et sku (WEB)
   - Pas de colonne commune directe
   - La colonne `id_web` dans LIAISON doit correspondre à `sku` dans WEB
   - Type de relation : potentiellement 1:1 après nettoyage

### Clés identifiées
- **ERP** : `product_id` (clé primaire)
- **LIAISON** : `product_id` (clé étrangère vers ERP)
- **LIAISON** : `id_web` (clé étrangère vers WEB.sku)
- **WEB** : `sku` (clé primaire après nettoyage)

---

## 5. PROBLEMES IDENTIFIES ET ACTIONS REQUISES

### Fichier ERP
- Pas de problème majeur
- Actions : Aucune, fichier propre

### Fichier LIAISON
- **Observation** : 91 valeurs manquantes sur id_web (11%)
  - **Action VALIDEE** : NE PAS supprimer les lignes avec id_web NULL à cette étape
  - **Action** : Dédoublonner uniquement (drop_duplicates)
  - **Résultat attendu** : 825 lignes après dédoublonnage
  - **Note** : Les NULL sur id_web seront supprimés APRES la jointure avec ERP

### Fichier WEB
- **Problème 1** : 85 valeurs manquantes sur sku (5.6%)
  - **Action VALIDEE** : Supprimer les lignes avec sku NULL
  
- **Problème 2** : Fichier contient des attachments en plus des produits
  - **Action VALIDEE** : Filtrer sur post_type = 'product'
  
- **Problème 3** : 798 doublons sur sku (714 valeurs uniques)
  - **Action VALIDEE** : Dédoublonner sur la colonne sku (drop_duplicates(subset=['sku']))
  
- **Problème 4** : Nombreuses colonnes inutiles avec 100% de valeurs manquantes
  - **Action** : Conserver uniquement les colonnes utiles (sku, total_sales, post_title, etc.)

- **Résultats VALIDES** :
  - Après filtrage products + suppression NULL sku + dédoublonnage : 714 lignes
  - Note : La valeur intermédiaire "1428 lignes" du contexte n'est pas confirmée

### Jointures
- **Jointure 1** : ERP + LIAISON sur product_id
  - Résultat attendu : 825 lignes (après nettoyage des deux fichiers)
  
- **Jointure 2** : (ERP + LIAISON) + WEB sur id_web = sku
  - Résultat attendu : 714 lignes (jointure finale)

---

## 6. VALEURS DE REFERENCE A VALIDER

Selon le contexte fourni, les valeurs attendues après traitement sont :
- ERP après dédoublonnage : **825 lignes**
- Liaison après dédoublonnage : **825 lignes**
- Web après nettoyage : **1428 lignes**
- Web après dédoublonnage : **714 lignes**
- Fichier fusionné final : **714 lignes**
- Chiffre d'affaires total : **70 568,60 €**
- Nombre de vins premium (z-score > 2) : **30 vins**

---

## 7. PLAN DE TRAITEMENT DES DONNEES (VALIDE)

### Etape 1 : Nettoyage ERP
- Pas d'action requise (fichier déjà propre)
- Dédoublonner (drop_duplicates) par sécurité
- **Résultat VALIDE : 825 lignes**

### Etape 2 : Nettoyage LIAISON
- **IMPORTANT : NE PAS supprimer les lignes avec id_web NULL**
- Dédoublonner uniquement (drop_duplicates)
- **Résultat VALIDE : 825 lignes**

### Etape 3 : Nettoyage et dédoublonnage WEB
- Filtrer sur post_type = 'product'
- Supprimer les lignes avec sku NULL (dropna(subset=['sku']))
- Dédoublonner sur sku (drop_duplicates(subset=['sku']))
- Supprimer les colonnes inutiles (optionnel)
- **Résultat VALIDE : 714 lignes**

### Etape 4 : Jointure ERP + LIAISON
- Jointure INNER sur product_id
- **Résultat : 825 lignes**

### Etape 5 : Suppression des NULL sur id_web
- Supprimer les lignes avec id_web NULL du résultat ERP+LIAISON
- **Résultat : 734 lignes**

### Etape 6 : Jointure finale avec WEB
- Convertir id_web et sku en string
- Jointure INNER sur id_web (ERP+LIAISON) = sku (WEB)
- **Résultat VALIDE : 714 lignes**

### Etape 7 : Calculs et validations
- Calcul du CA par produit : CA = price × total_sales
- Calcul du CA total : **VALIDE = 70 568,60 €**
- Calcul du z-score sur les prix : z = (price - mean) / std
- Classification premium/ordinaire (z-score > 2)
- **Nombre de vins premium VALIDE : 30 vins**

---

## 8. COLONNES UTILES IDENTIFIEES

### Pour le calcul du CA
- `price` (ERP)
- `total_sales` (WEB)
- CA = price × total_sales

### Pour la classification des vins
- `price` (ERP)
- Calcul : z-score = (price - mean(price)) / std(price)
- Premium si z-score > 2

### Pour les rapports
- `product_id` (identification)
- `post_title` (nom du vin)
- `price` (prix)
- `total_sales` (quantité vendue)
- CA calculé
- Classification (premium/ordinaire)

---

## CONCLUSION

L'analyse des fichiers sources révèle :
1. **ERP** : Fichier propre, prêt à l'emploi
2. **LIAISON** : Les valeurs NULL sur id_web doivent être conservées jusqu'après la jointure avec ERP
3. **WEB** : Nécessite un nettoyage (filtrage products, suppression NULL sku, dédoublonnage)

Le processus de réconciliation validé : ERP → LIAISON (conserver NULL) → Jointure → Supprimer NULL id_web → Jointure avec WEB