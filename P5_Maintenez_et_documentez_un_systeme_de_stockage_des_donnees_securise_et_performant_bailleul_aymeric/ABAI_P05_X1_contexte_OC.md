# Mission — Migrez des données médicales à l'aide du NoSQL

## Comment allez-vous procéder ?

Cette mission suit un scénario de projet professionnel.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?

Vous débutez en tant que stagiaire Data Engineer dans l'entreprise **DataSoluTech**. Vous prenez vos fonctions sous la responsabilité de **Boris**, votre chef de projet.

DataSoluTech est spécialisé dans la fourniture de solutions de gestion de données et d'analyse pour tous types d'entreprises. L'entreprise aide ses clients à exploiter leurs données pour améliorer leur prise de décision, optimiser leurs opérations et augmenter leur efficacité.

## Vous recevez un mail de Boris :

```
De : Boris
À : Moi
Objet : Nouvelle mission excitante - Migration des données médicales vers MongoDB et déploiement sur AWS

Salut,

J'espère que tu vas bien !

Je pense avoir trouvé une mission très intéressante pour toi. Nous venons de recevoir un dataset de données médicales de patients (voir P.J) d'un de nos clients. Ils commencent à avoir des soucis de scalabilité avec leurs tâches quotidiennes et ont besoin de notre aide.

Pour les aider à mieux gérer leurs données, nous leur avons proposé une solution Big Data scalable horizontalement. C'est là que tu interviens, voici ce que j'aimerais que tu fasses :

La migration des données vers MongoDB via Docker :
- Rédige un script afin d'automatiser la migration du dataset reçu vers MongoDB.
- Utilise Docker pour conteneuriser MongoDB ainsi que le(s) script(s) de migration des données afin que le tout soit portable et scalable.
- N'oublie pas de versionner et de sauvegarder ton travail via GitHub.
- Assure-toi de bien documenter ton travail par un readme détaillé sur la page d'accueil du GitHub.
- Inclus le schéma de la base de données dans ta documentation.
- Décris bien le système d'authentification ainsi que les rôles utilisateurs que tu créeras.

Les recherches autour du déploiement sur le cloud AWS :
- Explore les options pour notre client pour déployer MongoDB sur AWS en effectuant des recherches.
- Mets en avant les avantages des services AWS comme Amazon S3, RDS pour MongoDB, Amazon DocumentDB, et Amazon ECS.

Quand tu auras terminé, prépare une présentation de type PowerPoint. Présente-moi l'intégralité de ton travail (de la migration à tes recherches sur le cloud) avant la réunion avec le client, en incluant :
- le contexte de la mission ;
- la description de ta démarche technique complète ;
- la justification de tes choix.

Cette mission est super importante pour renforcer notre relation avec ce client, et je suis sûr que tu peux t'en charger. Si tu as des questions ou besoin de plus d'infos, n'hésite surtout pas à me demander.

Merci beaucoup pour ton très bon travail et ton dévouement.

À bientôt,
Boris

P.J: Dataset données médicales
```

Cette mission est entièrement guidée. Vous pouvez suivre les étapes ci-dessous.

## Étape 1 - Faites la migration vers MongoDB

### Prérequis
- Avoir consulté les ressources pédagogiques sur le NoSQL.

### Résultats attendus
- Un script permettant, lorsqu'il est exécuté, de transférer les données du CSV dans la base de données MongoDB.
- Un Readme expliquant la logique de la migration et comment fonctionne le script.
- Un requirements.txt contenant tous les modules (et leur version) nécessaires au bon fonctionnement de votre environnement virtuel.

### Recommandations
- Documentez systématiquement votre travail.
- Installez MongoDB en local.
- Définir les concepts clés de MongoDB : Documents, Collections, Bases de données.
- Créer et manipuler des collections et documents MongoDB en utilisant quelques exemples pris dans votre dataset.
- Utiliser les commandes de base pour CRUD (Create, Read, Update, Delete) dans MongoDB via un script Python.
- Tester l'intégrité des données (colonnes disponibles, types des variables, doublons, valeurs manquantes...) avant et après la migration.
- Automatiser le processus de test.
- Importer et exporter l'ensemble des données en MongoDB.

### Outils
- MongoDB

### Points de vigilance
- Portez attention au typage des champs.
- Mettre en place des index pertinents.

### Ressources
- Article: An Introduction to Python Unit Testing with unittest and pytest
- Article: Getting Started With Testing in Python

## Étape 2 - Conteneurisez l'application avec Docker

### Prérequis
- Avoir lu le cours "Optimisez votre déploiement en créant des conteneurs avec Docker".

### Résultat attendu
- Un docker-compose permettant de déployer et d'exécuter votre migration de données au sein de différents conteneurs et/ou volumes.
- Vous devrez pouvoir démontrer sur demande que votre migration fonctionne bien.

### Recommandations
- Installer Docker et Docker Compose sur votre machine.
- Créer des volumes pour pouvoir y mettre vos données (à minima : 1 pour le CSV et 1 pour la base de données).
- Définir un fichier docker-compose.yml qui permet de gérer vos conteneurs et vos volumes dans un seul fichier.
- S'assurer que l'application MongoDB conteneurisée est fonctionnelle.

### Outils
- Docker

### Points de vigilance
- Être capable d'expliquer la différence entre un conteneur et une machine virtuelle.
- Import des images Docker appropriées.
- Utilisation d'au moins un volume.
- Bonne compréhension du démon docker (et de ses limites).

## Étape 3 - Explorez AWS

Cette étape vous permet de vous familiariser avec un sujet qui sera retravaillé ultérieurement dans le parcours. Elle ne fera pas l'objet d'une évaluation par l'évaluateur dans ce projet. Néanmoins, effectuez cette étape et échangez avec votre mentor sur vos résultats.

### Prérequis
- Avoir compris les différences entre un ordinateur et un serveur.
- Avoir lu la ressource "Qu'est-ce que le stockage dans le cloud ?".

### Résultat attendu
- Une documentation des recherches effectuées permettant de bien expliquer au client l'utilité du passage au cloud et les services disponibles chez AWS.
- Il ne s'agit pas de réaliser le déploiement cloud mais de vous documenter sur le sujet.

### Recommandations
Renseignez-vous et documentez vos recherches sur :
- Méthode pour créer un compte AWS
- Tarifications d'AWS
- Amazon RDS pour MongoDB et Amazon DocumentDB (compatible MongoDB)
- Déploiement d'une instance MongoDB dans un conteneur Docker sur Amazon ECS (Elastic Container Service)
- Configuration des sauvegardes et surveillance des bases de données sur AWS

## Étape 4 - Concevez votre support de présentation

### Prérequis
- Avoir finalisé votre travail.

### Résultat attendu
- Un support de présentation rappelant :
  - le contexte de la mission ;
  - la description de votre démarche technique complète ;
  - la justification de vos choix.

### Recommandations
- Privilégiez l'utilisation de schémas plutôt que de texte pour expliquer les technologies choisies.

## Étape 5 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.
- Livrables et soutenance
