## 📊 Aide-Mémoire Power BI

### 1\. 📥 Obtenir et Transformer les Données (Power Query)

| Action | Où le trouver | But / Fonction Clé |
| :--- | :--- | :--- |
| **Obtenir les données** | Ruban *Accueil* de Power BI Desktop | Connecte Power BI à diverses sources (Excel, SQL, Web, etc.). |
| **Transformer les données** | Ruban *Accueil* \> *Transformer les données* | Ouvre l'**Éditeur Power Query**. |
| **Éditeur Power Query** | Fenêtre séparée | Nettoyage, mise en forme et transformation des données. |
| **Supprimer/Renommer des colonnes** | Clic droit sur l'en-tête de colonne | Suppression des données inutiles. |
| **Types de données** | Icône à gauche de l'en-tête de colonne | Changement du type (Texte, Nombre décimal, Date, etc.) - **Crucial pour les calculs.** |
| **Fusionner des requêtes** | Onglet *Accueil* de Power Query | Équivalent d'une jointure (JOIN) SQL pour combiner des tables horizontalement. |
| **Ajouter des requêtes** | Onglet *Accueil* de Power Query | Empile des tables avec des structures similaires (UNION SQL). |

-----

### 2\. 🧩 Modélisation des Données

| Concept | Vue dans Power BI Desktop | Description |
| :--- | :--- | :--- |
| **Vue Modèle** | Icône de trois rectangles liés | Où vous créez et gérez les relations. |
| **Relations** | Lignes entre les tables | Connecte les tables sur des colonnes clés (ex: `ID_Produit`). |
| **Cardinalité** | $1:M$ (Un-à-plusieurs) **(La plus courante)**, $1:1$, $M:M$. | Définit le type de jointure. $1:M$ est essentiel pour l'analyse. |
| **Direction du filtre** | Flèche sur la ligne de relation | Comment les filtres circulent entre les tables. Par défaut : côté $1$ vers côté $M$. |
| **Table de Faits** | N/A (Concept) | Contient les données transactionnelles ou mesurables (Ventes, Commandes). |
| **Table de Dimensions** | N/A (Concept) | Contient des attributs descriptifs (Clients, Produits, Dates). |
| **Masquer dans le rapport** | Clic droit sur la colonne | Cache les colonnes clés (ID) pour un utilisateur final plus propre. |

-----

### 3\. ✍️ DAX (Data Analysis eXpressions)

Le langage de formule de Power BI. Utilisé pour créer de nouvelles **Mesures** et **Colonnes calculées**.

#### Concepts Fondamentaux DAX

| Élément | Syntaxe et Exemple | Usage |
| :--- | :--- | :--- |
| **Mesure** | `Total Ventes = SUM('Ventes'[Montant])` | **Agrégation** qui se recalcule en fonction du contexte du filtre (le plus utilisé). |
| **Colonne Calculée** | `Année = YEAR('Date'[Date Complète])` | Calcul effectué ligne par ligne dans la table (à éviter si une Mesure est possible). |
| **Contexte de filtre** | N/A (Concept) | Les filtres appliqués par les visuels, les segments ou les relations. |
| **Contexte de ligne** | N/A (Concept) | La ligne actuelle dans laquelle la formule est évaluée (utilisé pour les Colonnes calculées et les fonctions d'itération X, ex: `SUMX`). |

#### Fonctions DAX Essentielles

| Fonction | Catégorie | Description |
| :--- | :--- | :--- |
| **`CALCULATE`** | Modification du Contexte | **La fonction la plus puissante.** Évalue une expression dans un **contexte de filtre modifié**. |
| **`FILTER`** | Table | Renvoyer un sous-ensemble d'une table, utilisé **à l'intérieur** de `CALCULATE`. |
| **`ALL` / `ALLEXCEPT`** | Modification du Contexte | Efface tous les filtres (ou tous sauf certains) d'une table/colonne. |
| **`RELATED`** | Relation | Extrait une colonne de la table *Un* dans une colonne calculée sur la table *Plusieurs*. |
| **`COUNTROWS`** | Agrégation | Compte le nombre de lignes dans une table. |
| **`SUMX` / `AVERAGEX`** | Itérateur (X) | Exécute une expression ligne par ligne puis agrège (ex: Calculer le total des ventes avant taxes \* Prix). |
| **`DATEADD`** | Intelligence Temporelle | Déplace le contexte temporel (ex: `CALCULATE(SUM( ... ), DATEADD('Date'[Date], -1, YEAR))`). |

-----

### 4\. 📈 Création de Rapports et Visuels

| Élément | Vue dans Power BI Desktop | Règle d'or |
| :--- | :--- | :--- |
| **Vue Rapport** | Icône du graphique à barres | L'interface principale de construction des tableaux de bord. |
| **Volet *Visualisations*** | Côté droit | Choisir le type de graphique, glisser les champs. |
| **Segment (Slicer)** | Type de visuel | Applique des filtres interactifs (dates, catégories, etc.). |
| **Visuels de Table/Matrice** | Types de visuels | Affiche des données détaillées (Matrice permet des groupements hiérarchiques). |
| **Graphique en courbes/barres** | Types de visuels | Idéal pour l'analyse des tendances ou la comparaison de catégories. |
| **Propriété *Info-bulles*** | Volet Visualisations | Champs qui apparaissent lorsque vous survolez un point de données (utile pour des détails supplémentaires). |
| **Interaction des visuels** | Ruban *Format* \> *Modifier les interactions* | Définir si un visuel doit filtrer ou mettre en évidence d'autres visuels. |

<br>

Aimeriez-vous que je vous donne un exemple spécifique de formule DAX ou que je vous montre comment établir une relation entre deux tables ?