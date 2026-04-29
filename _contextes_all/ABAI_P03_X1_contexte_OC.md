# Exercice — Entraînez-vous avec SQL et créez votre BDD

## Comment allez-vous procéder ?

Tout au long de cet exercice en 3 parties, vous serez **Data Engineer** chez **Laplace Immo, un réseau national d'agences immobilières**. Cette entreprise accorde une importance particulière à l'utilisation des données afin de se démarquer de la concurrence.

Vous serez en charge d'un nouveau projet dans lequel vous allez **collecter** l'ensemble des transactions immobilières en France. Cela permettra entre autres de suivre l'évolution du prix au mètre carré et d'identifier les régions où le marché est le plus porteur. Vous utiliserez ensuite cette base pour **analyser** le marché et **répondre aux besoins** de votre entreprise.

L'agence souhaite faire un premier test sous forme d'un **Proof Of Concept (POC)**.

À l'issue des 3 parties de cet exercice, vous aurez réalisé deux livrables :
- Un **dictionnaire des données** complété au format tableur
- Un **support de présentation** (Google Slides ou PowerPoint) contenant :
  - le contexte du projet ;
  - la transformation des données ;
  - un extrait du dictionnaire des données ;
  - le schéma relationnel normalisé ;
  - une capture d'écran de la base de données avec les tables créées et les données chargées ;
  - le code SQL des requêtes et leurs résultats.

Cette première partie est l'étape la plus importante de ce projet, car elle aura des répercussions jusqu'au SQL que vous allez écrire pour extraire vos données.

---

# Partie 1 — Comprenez des données et créez un schéma relationnel

## Étape 1 - Comprenez les données

### Prérequis
- Avoir suivi le cours sur la modélisation des bases de données.
- Avoir téléchargé les données et le modèle de dictionnaire des données.

### Résultats attendus
- Une bonne compréhension des types de données présentes dans le fichier.
- Un dictionnaire de données avec les données nécessaires, conformément à la réglementation RGPD et respectant la 3ème forme normale.

Pour chaque variable à conserver, remplir les colonnes correspondantes avec : un code, une signification, un type, une longueur, une nature, une règle de gestion, une règle de calcul (si nécessaire).

### Recommandations
- C'est particulièrement important de prendre du temps pour comprendre les données. Regardez dans chaque colonne les différentes données présentes.
- Ne jamais partir du principe qu'un dataset est à 100% fiable. Vérifier systématiquement si des informations peu fiables sont présentes.

### Outils
- Un tableur : Google Sheet ou Excel (solutions les plus simples).
- Un notebook Python si vous êtes à l'aise en programmation.

### Points de vigilance
- La compréhension des données est un facteur clé de réussite pour ce projet.
- Il est important de bien comprendre les **lois normales** dans les bases de données (1NF, 2NF, 3NF).
- Pour être conforme à la 1NF, les données doivent être atomiques (indivisibles sans perdre leur sens).

### Ressources
- "Améliorez votre modélisation grâce aux formes normales" — cours Modélisez vos bases de données.

## Étape 2 - Créez le schéma relationnel

### Instructions
- Réalisez le schéma de votre base de données (à partir de l'ébauche du schéma relationnel fournie, ou créez votre propre schéma).
- La finalité du projet est d'arriver à répondre aux **besoins en analyse** de l'entreprise. Consultez le compte-rendu de réunion pour connaître ces besoins.

### Prérequis
- Avoir réalisé le dictionnaire des données.
- Être capable d'expliquer la 3ème forme normale.
- Avoir téléchargé l'ébauche du schéma relationnel (si nécessaire).

### Résultat attendu
- Le schéma relationnel mis à jour avec les informations supplémentaires (ou votre propre schéma).

### Recommandations
- Utilisez l'ébauche du schéma comme base de départ.
- Vous devez être en mesure de **choisir les variables indispensables** pour répondre à l'ensemble des **besoins** de votre entreprise.
- Le choix de vos clés primaires et étrangères devra être justifié en session bilan.

### Outils
- **SQL Power Architect** (recommandé — permet de modéliser la BDD et de générer automatiquement le code SQL).
- Alternatives : Draw.io, Looping.

### Points de vigilance
- Les clés de votre base de données peuvent être une **concaténation** de plusieurs données (ex: id_codedep_codecommune "34172" = code département "34" + code commune "172").

### Ressources
- SQL Power Architect : https://bestofbi.com/architect-download/
- Fiche sur les MPD : https://www.base-de-donnees.com/mpd/

## Étape 3 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.

---

# Partie 2 — Créez une base de données et chargez des données

## Étape 1 - Créez la base de données

### Résultat attendu
- Une base de données (SQLite Studio, PostgreSQL, ou MySQL) conforme au schéma relationnel.
- Respect des formes normales : 1NF, 2NF, 3NF.
- Clés primaires uniques définies.

### Outils
- SQLite Studio, PostgreSQL, ou MySQL

## Étape 2 - Chargez les données

### Résultat attendu
- Les données CSV chargées dans la base de données.
- Toutes les données essentielles présentes et vérifiées.

### Points de vigilance
- Préparez les fichiers CSV pour respecter les contraintes de la base (unicité des clés primaires).

## Étape 3 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.

---

# Partie 3 — Utilisez du SQL pour extraire des données

## Contexte

Laplace Immo réseau national agences immobilières — compte-rendu de réunion avec les besoins SQL de l'agence.

## Étape 1 - Créez les requêtes SQL

### Résultat attendu
- Des requêtes SQL répondant aux besoins identifiés dans le compte-rendu de réunion.
- Utilisation d'alias, de sous-requêtes, de tables temporaires.

### Outils
- SQLite Studio, PostgreSQL ou MySQL

## Étape 2 - Préparez le support de présentation

### Résultat attendu
- Un support de présentation incluant : contexte, schéma relationnel, code des requêtes SQL et leurs résultats.

## Étape 3 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.
