# Mission — Construisez et testez une infrastructure de données

## Comment allez-vous procéder ?

Cette mission suit un scénario de projet professionnel.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?

Vous êtes Data Engineer chez **GreenAndCoop**, un fournisseur coopératif d'électricité renouvelable dans les Hauts-de-France. Vous travaillez sur le projet **Forecast 2.0**, qui vise à intégrer des données de stations météo semi-professionnelles pour améliorer les prédictions de production d'énergie.

## Vous recevez un mail d'Ouly (cheffe de projet Forecast 2.0, équipe Data Science) :

```
De : Ouly
À : Moi
Objet : Projet Forecast 2.0 - périmètre et stack technique

Bonjour,

Pour le projet Forecast 2.0, voici les sources de données retenues :
- Réseau InfoClimat : stations de Bergues, Hazebrouck, Armentières, Lille-Lesquin
- Weather Underground : IICHTE19 WeerstationBS Ichtegem (BE, 51.092N 2.999E, 15m alt.) et ILAMAD25 La Madeleine (FR, 50.659N 3.07E, 23m alt.)

Stack imposée par l'équipe :
- Airbyte → PostgreSQL (ELT)
- DBT pour les transformations
- Stockage sur AWS PostgreSQL
- SageMaker utilisé par l'équipe Data Science pour le ML

Délai : réunion dans 1 mois.

Livrables attendus :
- Schéma de la base de données (ERD)
- Logigramme du processus ELT
- Architecture globale
- Stack technique justifiée
- Rapport de contrôle qualité (taux d'erreurs)
- Délais de mise à disposition des données

Bonne continuation,
Ouly
```

Cette mission est entièrement guidée. Vous pouvez suivre les étapes ci-dessous.

## Étape 0 - Préparez l'environnement

### Résultats attendus
- Docker installé et fonctionnel.
- PostgreSQL déployé via Docker.
- Airbyte déployé via Docker Compose.
- DBT Core installé avec `dbt-postgres`.

### Outils
- Docker, Docker Compose, PostgreSQL, Airbyte, DBT Core

## Étape 1 - Récupérez les données météo avec Airbyte

### Résultats attendus
- Connecteurs InfoClimat et Weather Underground configurés dans Airbyte.
- Tables RAW créées dans PostgreSQL.
- Synchronisation des données opérationnelle.

### Points de vigilance
- La destination doit être PostgreSQL (ne pas modifier les données avant l'ingestion).
- Documenter la configuration des connecteurs.

## Étape 2 - Transformez les données avec DBT

### Résultats attendus
- Modèles DBT organisés en trois couches : staging → intermediate → marts.
- Schéma en étoile avec table de faits et dimensions (dont `dim_weather_stations`).
- Métadonnées des stations intégrées (ILAMAD25 La Madeleine et IICHTE19 Ichtegem).

### Outils
- DBT Core, dbt-postgres, PostgreSQL

## Étape 3 - Optimisez et sécurisez le schéma PostgreSQL

### Résultats attendus
- Index créés au niveau des modèles marts dans DBT.
- Contraintes d'unicité définies.

### Recommandations
- Définir les index dans DBT via `config()` ou `dbt_project.yml`.

## Étape 4 - Mettez en place les tests qualité et la documentation DBT

### Résultats attendus
- Tests DBT définis pour les modèles (unicité, non-nullité, cohérence).
- Documentation des modèles générée avec `dbt docs generate`.

## Étape 5 - Déployez sur AWS

### Résultats attendus
- Instance PostgreSQL sur AWS.
- Pipeline ELT fonctionnel en production sur AWS.

## Étape 6 - Concevez le support de présentation et préparez la soutenance

### Résultat attendu
Un support de présentation incluant :
- Contexte du projet
- Démarche technique et justification des choix
- Schéma ERD de la base de données
- Logigramme du processus ELT
- Architecture globale (Airbyte → PostgreSQL → DBT → AWS)
- Captures de la configuration Airbyte et du lineage DBT
- Rapport de qualité (taux d'erreurs)
- Capture de l'environnement AWS

## Étape 7 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.
