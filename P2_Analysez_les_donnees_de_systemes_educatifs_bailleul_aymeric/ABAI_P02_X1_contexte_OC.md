# Exercice — Analysez des données de systèmes éducatifs

## Comment allez-vous procéder ?

Cet exercice en 3 parties suit un scénario de projet professionnel.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?

Vous êtes Data Scientist au sein d'une start-up EdTech nommée **academy**, qui aspire à se développer à l'international. Votre manager, **Mark**, souhaite identifier les pays avec un fort potentiel pour les services de formation en ligne, en se basant sur des données de la **Banque Mondiale** sur l'éducation dans le monde.

Cette mission est entièrement guidée. Vous pouvez suivre les étapes ci-dessous.

---

# Partie 1 — Analysez des données de systèmes éducatifs

## Étape 1 - Chargez les données dans votre Notebook

### Prérequis
- Avoir suivi les cours sur les librairies Python pour la Data Science.
- Avoir installé JupyterLab et créé un environnement virtuel.
- Avoir téléchargé les 5 fichiers de données de la Banque Mondiale.

### Résultat attendu
- Un notebook Jupyter contenant le code de chargement des 5 fichiers (CSV, XLS ou ZIP) dans des DataFrames Pandas.
- Un markdown au début du notebook expliquant le contexte du projet.

### Recommandations
- Utilisez la méthode `pd.read_csv()` ou `pd.read_excel()`.
- Documentez votre code avec des cellules Markdown.

### Outils
- JupyterLab
- Pandas

### Points de vigilance
- Vérifiez l'encodage des fichiers (UTF-8, Latin-1...).

## Étape 2 - Collectez des informations basiques sur chaque jeu de données

### Prérequis
- Avoir chargé les 5 fichiers de données.

### Résultat attendu
- Pour chaque fichier : dimensions (lignes/colonnes), types des colonnes, nombre de doublons, nombre de valeurs manquantes par colonne, statistiques descriptives via `describe()`.
- Pour les colonnes catégorielles : nombre d'occurrences de chaque valeur.

### Recommandations
Réutilisez le plus possible les méthodes déjà implémentées dans Pandas :
- `head()`, `shape`, `unique()`, `duplicated()`, `drop_duplicates()`, `value_counts()`, `info()`, `isnull()`, etc.
- Traitez chaque fichier de données l'un après l'autre.
- Si vous rencontrez des erreurs de code que vous ne comprenez pas, copiez le message d'erreur et cherchez sur StackOverflow.
- Nous vous déconseillons à ce stade d'utiliser ChatGPT (ou un équivalent) pour débugger votre code.

### Outils
- Pandas

## Étape 3 - Réalisez votre premier nettoyage

### Résultat attendu
- Code permettant de filtrer les faux pays des tables où cela fait sens (Country, Country-Series, FootNote et Data).
- Markdown associé au code pour expliquer l'approche.

### Instructions
- Regardez de plus près les lignes du fichier Country pour identifier des faux pays.
- Supprimez les lignes correspondantes du dataframe contenant la donnée Country.
- Utilisez les 2 méthodes suivantes pour supprimer les faux pays des autres dataframes :
  - En stockant les faux pays dans une liste qui sera utilisée pour le filtrage des différents dataframes.
  - En utilisant un inner join entre les pays du dataframe Country nettoyé, et les autres dataframes.

### Recommandations
- L'objectif est de déterminer si le jeu de données Country contient bien ce qu'il est censé contenir : des informations sur des pays.
- Utilisez le filtrage à base de conditions avec Pandas : `df[ ~df[colonne].isin(liste_mauvaises_valeurs) ]`
- L'utilisation du caractère `~` permet d'inverser la condition spécifiée à Pandas lors du filtrage.
- Utilisez des markdowns pour bien organiser votre notebook.

### Points de vigilance
- Évitez l'utilisation d'`iloc` pour supprimer des lignes ou des colonnes sur la base d'une position d'index (hardcoding).
- Les années jouent un rôle central dans l'organisation de nos données : quelles années conserver, comment gérer les valeurs manquantes, comment les organiser.

### Ressources
- Chapitre "Filtrez les données du data frame" du cours "Découvrez les librairies Python pour la Data Science".

## Étape 4 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la partie 1 de la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.

---

# Partie 2 — Réduisez le périmètre d'analyse

## Étape 1 - Réduisez le périmètre d'analyse : approche métier

### Résultat attendu
- Un notebook avec le code permettant de filtrer les pays et indicateurs pertinents selon une approche métier.

### Recommandations
- Utilisez `value_counts()`, `isin()`, `np.arange()` pour cibler les pays et des indicateurs pertinents.

### Outils
- Pandas, NumPy

## Étape 2 - Réduisez le périmètre d'analyse : approche data

### Résultat attendu
- Un code calculant le taux de remplissage pour chaque colonne (indicateur) afin d'éliminer ceux avec trop de données manquantes.

### Outils
- Pandas

## Étape 3 - Consolidez les résultats dans un DataFrame pays/indicateurs

### Résultat attendu
- Un DataFrame consolidé avec les pays en index et les indicateurs retenus en colonnes, via `pivot_table()`.

### Outils
- Pandas (`pivot_table`)

## Étape 4 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la partie 2 de la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.

---

# Partie 3 — Analysez vos données et faites votre présentation

## Étape 1 - Identifiez des indicateurs redondants

### Résultat attendu
- Une analyse de corrélation entre indicateurs (méthodes de Pearson et/ou Spearman).
- Une heatmap de corrélation.
- Une liste d'indicateurs non-redondants à conserver.

### Outils
- Pandas, Scipy (corrélation), Seaborn/Matplotlib (heatmap)

## Étape 2 - Analysez les indicateurs restants et formulez une liste de pays pertinents

### Résultat attendu
- Des graphiques d'analyse univariée et bivariée pour les indicateurs retenus.
- Une liste de pays pertinents à cibler pour le développement international d'academy.
- Un notebook structuré et commenté sur l'ensemble des analyses.

### Outils
- Pandas, Matplotlib, Seaborn

## Étape 3 - Formalisez vos résultats

### Résultat attendu
- Une présentation au format Google Slides ou PowerPoint incluant :
  - Contexte et problématique
  - Démarche analytique
  - Résultats et conclusions
  - Storytelling avec des graphiques clairs

### Recommandations
- Adaptez les graphiques (axes, titres, échelles et légendes) au message à transmettre.
- Mettez en place une logique de storytelling.

## Étape 4 - Rendez vos analyses reproductibles

### Résultat attendu
- Un environnement de développement reproductible via `uv` et `pyproject.toml`.
- Un fichier `pyproject.toml` listant les dépendances du projet.

### Outils
- uv, pyproject.toml

## Étape 5 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la partie 3 de la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.
