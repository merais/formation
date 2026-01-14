# Compréhension du processus métier - P10 BottleNeck

## 1. PROCESSUS DE RECONCILIATION VIA LE FICHIER LIAISON

### Contexte métier
BottleNeck utilise deux systèmes distincts :
- **ERP** : Système de gestion interne (stocks, prix, références produits)
- **CMS Web** : Plateforme de vente en ligne WordPress/WooCommerce

Le **fichier LIAISON** fait le pont entre ces deux systèmes qui n'utilisent pas les mêmes identifiants.

### Schéma de réconciliation

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  ERP            │         │  LIAISON         │         │  WEB (CMS)      │
│                 │         │                  │         │                 │
│  product_id ─── ┼────────►│  product_id      │         │                 │
│  (clé ERP)      │         │  (clé ERP)       │         │                 │
│                 │         │                  │         │                 │
│  price          │         │  id_web ─────────┼────────►│  sku            │
│  stock          │         │  (clé Web)       │         │  (clé Web)      │
│  ...            │         │                  │         │                 │
│                 │         │                  │         │  total_sales    │
│                 │         │                  │         │  post_title     │
│                 │         │                  │         │  ...            │
└─────────────────┘         └──────────────────┘         └─────────────────┘
```

### Étapes de réconciliation validées

1. **Étape 1 : Jointure ERP + LIAISON**
   - Clé : `product_id`
   - Type : INNER JOIN
   - Résultat : 825 lignes (tous les produits ERP avec leur référence web)

2. **Étape 2 : Suppression des produits sans référence web**
   - Condition : `id_web IS NOT NULL`
   - Résultat : 734 lignes (produits vendus en ligne uniquement)

3. **Étape 3 : Jointure avec WEB**
   - Clé : `id_web` (LIAISON) = `sku` (WEB)
   - Type : INNER JOIN
   - Résultat : 714 lignes (produits avec historique de ventes)

### Pourquoi ce processus ?

**Question métier** : Pourquoi ne pas joindre directement ERP et WEB ?
**Réponse** : Les systèmes ERP et WEB utilisent des identifiants différents et incompatibles. Le fichier LIAISON est la **table de correspondance** qui permet de faire le lien.

**Question métier** : Pourquoi conserver les NULL dans LIAISON ?
**Réponse** : Certains produits ERP n'ont pas encore de référence web (nouveaux produits, produits en préparation). On conserve 825 lignes pour garder la cohérence avec l'ERP, puis on filtre selon les besoins métier.

---

## 2. REGLES METIER POUR LE CALCUL DU CHIFFRE D'AFFAIRES

### Formule du chiffre d'affaires

```
CA par produit = Prix unitaire × Quantité vendue
CA par produit = price (ERP) × total_sales (WEB)
```

### Sources des données

| Donnée | Source | Fichier | Colonne |
|--------|--------|---------|---------|
| Prix unitaire | ERP | Fichier_erp.xlsx | `price` |
| Quantité vendue | WEB | Fichier_web.xlsx | `total_sales` |

### Agrégation du CA total

```
CA total = Somme (CA par produit)
CA total = Somme (price × total_sales)
```

**Valeur de référence validée** : **70 568,60 €**

### Règles métier importantes

1. **Produits non vendus** : Si `total_sales = 0`, alors `CA = 0`
   - Ces produits sont conservés dans le rapport (CA = 0 €)

2. **Produits sans référence web** : Ne sont pas inclus dans le calcul du CA
   - Seuls les produits présents dans WEB sont comptabilisés

3. **Arrondi** : Le CA est calculé avec 2 décimales (en euros)

4. **Période** : Les données `total_sales` représentent les ventes cumulées
   - Pas de notion de période dans les données actuelles
   - Le CA calculé est le CA total depuis le début

---

## 3. METHODE DE CLASSIFICATION DES VINS (Z-SCORE)

### Définition du z-score

Le **z-score** (ou score standardisé) mesure l'écart d'une valeur par rapport à la moyenne, exprimé en nombre d'écarts-types.

### Formule mathématique

```
z-score = (prix du vin - moyenne des prix) / écart-type des prix

Notation mathématique :
z = (x - mu) / sigma

Où :
- x = prix du vin
- mu  = moyenne des prix de tous les vins
- sigma = écart-type des prix de tous les vins
```

### Exemple avec les données BottleNeck

Statistiques calculées sur les 714 produits :
- **Moyenne (mu)** : 32,49 €
- **Écart-type (sigma)** : 27,81 €

**Exemple 1 : Vin ordinaire**
```
Prix : 24,20 €
z-score = (24,20 - 32,49) / 27,81
z-score = -8,29 / 27,81
z-score = -0,30

Classification : ORDINAIRE (z-score < 2)
```

**Exemple 2 : Vin premium**
```
Prix : 100,00 €
z-score = (100,00 - 32,49) / 27,81
z-score = 67,51 / 27,81
z-score = 2,43

Classification : PREMIUM (z-score > 2)
```

### Règle de classification

```
SI z-score > 2 ALORS
    Classification = PREMIUM
SINON
    Classification = ORDINAIRE
FIN SI
```

**Valeur de référence validée** : **30 vins premium** sur 714 produits (4,2%)

### Interprétation métier du z-score

| Z-score | Interprétation | Classification BottleNeck |
|---------|----------------|---------------------------|
| z < -2 | Prix très bas (< mu - 2sigma) | Ordinaire |
| -2 ≤ z ≤ 2 | Prix dans la norme (±2sigma) | Ordinaire |
| z > 2 | Prix très élevé (> mu + 2sigma) | **Premium** |

**Signification du seuil z > 2** :
- Environ 95% des vins ont un prix dans l'intervalle [mu - 2sigma, mu + 2sigma]
- Les vins avec z > 2 sont dans les 2,5% les plus chers
- Ce sont les vins "exceptionnels" ou "de prestige"

### Avantages de cette méthode

1. **Objectivité** : Classification basée sur des statistiques, pas de seuil arbitraire
2. **Relativité** : S'adapte automatiquement à la distribution des prix
3. **Standardisation** : Méthode reconnue et reproductible
4. **Outliers** : Détecte efficacement les valeurs atypiques (très chers)

---

## 4. CRITERES DE QUALITE DES DONNEES

### 4.1 Complétude

**Définition** : Les données nécessaires sont présentes et non manquantes.

**Critères BottleNeck** :
- **ERP** : Aucune valeur manquante acceptée
- **LIAISON** : Les valeurs manquantes sur `id_web` sont tolérées (produits non en ligne)
- **WEB** : Les valeurs manquantes sur `sku` sont éliminées (impossible de réconcilier)
- **WEB** : Les valeurs manquantes sur `total_sales` sont éliminées (données de vente requises)

**Règle métier** : Pour le calcul du CA, toutes les colonnes `price`, `total_sales`, `sku`, `id_web` doivent être présentes.

### 4.2 Unicité

**Définition** : Pas de doublons, chaque entité est unique.

**Critères BottleNeck** :
- **ERP** : `product_id` doit être unique (clé primaire)
- **LIAISON** : Pas de doublons complets tolérés
- **WEB** : `sku` doit être unique après dédoublonnage (clé primaire)

**Règle métier** : En cas de doublons sur `sku`, conserver la première occurrence.

### 4.3 Exactitude

**Définition** : Les données correspondent à la réalité.

**Critères BottleNeck** :
- **Prix** : Valeurs positives uniquement (`price > 0`)
- **Quantité** : Valeurs positives ou nulles (`total_sales ≥ 0`)
- **CA total** : Doit correspondre à la référence validée (70 568,60 €)
- **Vins premium** : Doit correspondre à la référence validée (30 vins)

### 4.4 Cohérence

**Définition** : Les données sont cohérentes entre elles et avec les règles métier.

**Critères BottleNeck** :
- **Jointures** : Le nombre de lignes après jointure doit être ≤ au minimum des deux tables
- **Références** : Tout `id_web` dans LIAISON doit exister dans WEB.sku (après nettoyage)
- **Types** : `id_web` et `sku` doivent être convertis en string pour la jointure

**Règle de cohérence des jointures** :
```
ERP (825) + LIAISON (825) = 825 lignes
ERP+LIAISON (734 après NULL) + WEB (714) = 714 lignes
```

### 4.5 Validité

**Définition** : Les données respectent les formats et contraintes attendus.

**Critères BottleNeck** :
- **product_id** : Type entier (int64)
- **price** : Type décimal (float64), 2 décimales
- **sku** : Type chaîne (string)
- **total_sales** : Type décimal (float64)
- **post_type** : Valeurs autorisées : 'product', 'attachment'

---

### Livrables métier

1. **Rapport CA Excel** : 
   - Colonnes : product_id, post_title, price, total_sales, CA
   - CA total en bas du rapport
   
2. **Fichier vins premium CSV** :
   - Colonnes : product_id, post_title, price, z_score
   - Filtre : z_score > 2
   - 30 lignes attendues

3. **Fichier vins ordinaires CSV** :
   - Colonnes : product_id, post_title, price, z_score
   - Filtre : z_score ≤ 2
   - 684 lignes attendues (714 - 30)

### Utilisateurs finaux

- **Laure** (vins premium, clients entreprises) : Utilise le fichier vins premium pour ses campagnes marketing
- **Maria** (vins ordinaires, particuliers) : Utilise le fichier vins ordinaires pour ses campagnes marketing
- **Direction** : Utilise le rapport CA pour le pilotage de l'activité

---

## CONCLUSION

Le processus métier de BottleNeck repose sur :
1. **Réconciliation** : Lier les systèmes ERP et Web via le fichier LIAISON
2. **Calcul du CA** : Combiner prix (ERP) et ventes (Web) pour obtenir le chiffre d'affaires
3. **Classification** : Utiliser le z-score pour segmenter les vins premium vs ordinaires
4. **Qualité** : Garantir la complétude, l'unicité, l'exactitude et la cohérence des données

Les critères de qualité permettent de valider que le pipeline de transformation fonctionne correctement et produit des résultats fiables pour les équipes métier.