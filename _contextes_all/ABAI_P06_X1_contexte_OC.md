# Mission — Anticipez les besoins en consommation de bâtiments

## Comment allez-vous procéder ?

Cette mission suit un scénario de projet professionnel.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?

Vous travaillez en tant que Data Engineer pour la **ville de Seattle**. Pour atteindre son objectif de ville neutre en émissions de carbone en 2050, votre équipe s'intéresse de près à la consommation et aux émissions des bâtiments non destinés à l'habitation.

Des relevés minutieux ont été effectués par les agents de la ville en 2016. Ces relevés sont coûteux à obtenir, et à partir de ceux déjà réalisés, vous voulez tenter de prédire les émissions de CO2 et la consommation totale d'énergie de bâtiments non destinés à l'habitation pour lesquels elles n'ont pas encore été mesurées.

Votre prédiction se basera sur les données structurelles des bâtiments (taille et usage des bâtiments, date de construction, situation géographique...).

Le Project Lead **Douglas** vous convie par message à une réunion de kick-off :

```
"Comme tu le sais, ce genre de projet est mené en général par ta collègue Data Scientist Léa. Sauf qu'elle va partir en congé maternité à partir de la semaine prochaine. Ce projet a une très haute visibilité en ce moment auprès de la mairie de Seattle et nous ne pouvons pas attendre son retour pour commencer à travailler dessus.

Afin de t'aider, je me suis coordonné avec Léa pour qu'elle te facilite le travail en te préparant un notebook avec un template de la démarche à suivre et des conseils pour éviter certains pièges.

Dans l'ensemble, j'attends de toi :
- une courte analyse exploratoire pour faire ressortir des insights clés sur les différents bâtiments ;
- des tests des différents modèles supervisés visant à prédire la consommation en énergie des bâtiments ;
- la détermination des facteurs principaux impactant le plus le modèle que tu auras sélectionné."
```

---

# Partie 1 — Prédisez la consommation d'énergie des bâtiments

## Étape 1 : Réalisez une analyse exploratoire

### Prérequis
- Avoir préparé un environnement virtuel Python avec tous les packages spécifiés dans la partie importation du notebook template.

### Résultat attendu
- Le notebook template avec la partie "Analyse exploratoire" complétée.

### Recommandations
- Bien lire tout d'abord l'énoncé pour se restreindre uniquement aux types pertinents de bâtiments.
- Identifier les colonnes qui peuvent aider à repérer des bâtiments aberrants ou peu pertinents.
- Il y a plusieurs colonnes candidates pouvant être une target du modèle. Il faut en choisir une pour tout le reste du projet.
- Bien choisir le type de graphique en fonction des features à comparer (quanti vs quanti, quanti vs quali, etc.).
- Conserver une trace du nombre de lignes avant et après un filtrage/nettoyage.

### Points de vigilance
- Ne pas supprimer toutes les lignes où une colonne présente une valeur manquante (trop peu de bâtiments pour la modélisation).
- Ne pas se précipiter vers l'analyse avant d'avoir bien compris le libellé et le contenu des colonnes.

### Ressources
- Chapitre "Améliorez un jeu de données" du cours d'initiation au ML.

## Étape 2 : Réalisez votre feature engineering

### Prérequis
- S'être familiarisé avec le jeu de données via l'analyse exploratoire.
- Avoir compris ce qu'est le feature engineering.

### Résultat attendu
- Le notebook template avec la partie "Feature Engineering" complétée.

### Recommandations
- Nous vous déconseillons fortement d'utiliser des outils comme ChatGPT pour cette section.
- Essayer de couvrir, dans la création des features, plusieurs catégories d'informations (localisation, temporalité, structure du bâtiment, etc.)
- Les valeurs des sources d'énergies (gaz, électricité) ne peuvent pas être utilisées (data leakage), mais rien ne vous empêche de créer des features indiquant quels types de sources d'énergie existent.

### Points de vigilance
- Attention au **data leakage** : on ne peut pas donner à un modèle de ML des features qui ne peuvent être calculées qu'en connaissant la consommation d'énergie.
- Se fixer à l'avance un certain nombre d'heures à ne pas dépasser sur cette partie.

## Étape 3 : Préparez les features pour la modélisation

### Prérequis
- Avoir complété l'étape 2.

### Résultats attendus
- Avoir complété la partie "Préparation des features pour la modélisation" du notebook template.
- Être capable d'expliquer votre démarche et votre logique jusqu'ici.

### Recommandations
- Si la méthode IQR ou z-score supprime trop de bâtiments outliers, utiliser des seuils sur la base de quantiles.
- Regarder l'ensemble des méthodes importées via scikit-learn par le template dans la section modélisation.
- Bien comprendre dans quelle situation on utilise un OneHotEncoder au lieu d'un LabelEncoder.

### Points de vigilance
- Éviter de réduire significativement la taille du dataset en supprimant les valeurs extrêmes : trouver le bon équilibre.
- Garder en tête que la matrice de corrélation n'est applicable que pour certains types de features.
- Ne pas utiliser le OneHotEncoder sur une feature qualitative à haute cardinalité.

## Étape 4 : Comparez plusieurs modèles supervisés

### Résultat attendu
- La partie "Comparaison de modèles" du notebook template complétée.
- Tableau récapitulatif des performances des modèles comparés.

### Outils
- scikit-learn

## Étape 5 : Optimisez et interprétez le modèle

### Prérequis
- Avoir terminé l'étape 4.

### Résultat attendu
- La partie "Optimisation et interprétation du modèle" du notebook template complétée.

### Recommandations
- Utiliser la méthode `GridSearchCV` importée plus haut dans le Notebook.
- Avant de lancer la Grid Search "à grande échelle", testez une petite grille de 10 combinaisons afin de vous assurer que votre code fonctionne.
- Il est de coutume de lancer la Grid Search "à grande échelle" une fois que l'on a fini la journée de travail.
- Il est coutume de représenter la feature importance sous forme d'un histogramme.

### Points de vigilance
- Limitez-vous à un maximum de 500 combinaisons différentes à tester (100 minimum si ordinateur peu puissant). Google Colab est une option.
- Ne pas s'intéresser à la feature importance avant d'avoir fini la phase d'optimisation du modèle.

## Étape 6 : Formalisez vos résultats

### Prérequis
- Avoir terminé l'étape 5.

### Résultat attendu
- Une présentation au format PPT claire et professionnelle présentant :
  - le contexte du projet ainsi que le contenu de la donnée ;
  - vos résultats d'analyse exploratoire ;
  - votre démarche de modélisation (préparation des données, évaluation des modèles, features importantes).

### Recommandations
- Partir du principe que l'audience ne suit pas le sujet d'aussi près que vous.
- Résumer les métriques de performances des modèles dans un tableau.
- Mettre en place une logique de storytelling.

### Points de vigilance
- Restez le plus concis possible.

---

# Partie 2 — Exposez votre modèle prédictif via une API

## Vous recevez un mail de Douglas :

```
De : Douglas
À : Moi
Objet : Suite du projet - API

Les performances du modèle sont rassurantes. Prépare une démo pour le comité de pilotage de la mairie de Seattle.
Outil suggéré : BentoML (notre collègue Léa l'a utilisé et recommande).
```

## Étape 1 : Définissez la logique API et testez en local

### Prérequis
- Avoir suivi le cours sur les API.
- Avoir un modèle ML entraîné et sauvegardé.

### Résultats attendus
- Un fichier `service.py` définissant l'API BentoML.
- Un fichier de validation (Pydantic ou Pandera).
- Une démonstration de l'API en local via `bentoml serve` et Swagger.

### Outils
- BentoML, Pydantic/Pandera

### Points de vigilance
- Ne pas confondre le format d'entrée utilisateur et les encodages internes du modèle.

## Étape 2 : Déployez votre API

### Résultats attendus
- Un fichier `bentofile.yaml` décrivant les dépendances.
- Une image Docker construite et déployée sur un service Cloud (AWS/GCP/Azure).

### Points de vigilance
- Arrêter le déploiement après les tests pour éviter des frais cloud.
- Ne pas utiliser `bentoclt` (déprécié).
