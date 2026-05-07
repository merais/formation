# Exercice — Concevez et analysez une base de données NoSQL

## Comment allez-vous procéder ?

Cet exercice en 3 parties suit un scénario de projet professionnel.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?

Vous travaillez pour l'association **NosCités**, qui étudie l'impact des grands événements sur les logements de courte durée (type Airbnb).

Suite à l'été des JO 2024, un crash de la base de données des locations de Paris est survenu et une sauvegarde a été récupérée au format MongoDB. Votre mission est d'analyser ces données pour produire un rapport sur **l'"effet JO 2024" sur les logements de courte durée à Paris**.

Cette mission est entièrement guidée. Vous pouvez suivre les étapes ci-dessous.

---

# Partie 1 — Comprenez les bénéfices du NoSQL

## Étape 1 - Importez les données

### Prérequis
- Avoir lu les cours NoSQL + MongoDB.
- Avoir téléchargé les données.

### Résultat attendu
- Les données importées dans MongoDB (captures d'écran).
- Une diapositive "Contexte" dans votre support de présentation.

### Outils
- `mongoimport` ou MongoDB Compass

## Étape 2 - Comprenez les données

### Résultat attendu
- Partie 1 du support de présentation complétée.
- Requêtes basiques : premier document, nombre de documents, nombre de logements.

### Recommandations
- Regardez les champs imbriqués dans les documents MongoDB.

### Points de vigilance
- La compréhension des données est un facteur clé de réussite pour ce projet.

---

# Partie 2 — Analysez une base de données NoSQL

## Étape 1 - Requêtez les données avec la CLI

### Résultat attendu
6 requêtes simples via `mongosh` :
- Nombre d'annonces par type de logement
- Top 5 des logements les plus évalués
- Nombre d'hôtes différents
- Nombre de locations instantanées disponibles
- Hôtes avec plus de 100 annonces
- Nombre de super hôtes

### Recommandations
- Consultez la documentation MongoDB section "Query".

### Outils
- `mongosh`

## Étape 2 - Utilisez Polars pour les requêtes complexes

### Résultat attendu
5 calculs statistiques avancés :
- Taux de réservation moyen par mois et par type de logement
- Médiane des avis pour tous les logements
- Médiane des avis par catégorie d'hôte
- Densité de logements par quartier
- Quartiers avec fort taux de réservation

### Outils
- pymongo + Polars

### Points de vigilance
- Distinguer les cas d'usage Polars vs MongoDB (Polars pour les analyses complexes côté Python).
- Faire attention à la syntaxe Polars vs celle de MongoDB.

## Étape 3 - Connectez la base à un outil BI

### Résultat attendu
- Connexion MongoDB à Power BI ou Tableau.
- Visualisations des résultats.

---

# Partie 3 — Concevez votre base de données

## Contexte
Les données de Lyon sont disponibles en plus de celles de Paris. Il faut les combiner et protéger la BDD pour l'avenir.

## Étape 1 - Importez les données dans la même collection

### Résultat attendu
- Tous les documents dans une seule collection, avec un paramètre permettant de distinguer Paris et Lyon.
- Ajouter le paramètre `ville` avant d'importer les données Lyon.

## Étape 2 - Répliquez les données avec un ReplicaSet

### Résultat attendu
- Base de données répliquée (arbitre inclus).
- Schéma avec connexion BI.
- Tableau récapitulatif du processus de réplication.

### Outils
- CLI MongoDB (plusieurs ports en local)

## Étape 3 - Distribuez les données avec le sharding

### Résultat attendu
- Cluster de shards créé.
- Collection distribuée (Paris et Lyon sur des shards différents).

### Outils
- CLI MongoDB

## Étape 4 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.
