# AWS

## 1. Méthode pour Créer un Compte AWS et Tarification

### Création d'un Compte AWS
La **création d'un compte AWS est gratuite** et donne accès à l'**Offre gratuite d'AWS**.
1.  Visitez la page d'inscription AWS.
2.  Vous devrez fournir une **carte bancaire** (pour la vérification d'identité et la prévention de la fraude), même si vous prévoyez d'utiliser uniquement les services gratuits.
3.  Une fois le compte créé, il est crucial de configurer un **budget de coût** (par ex., 1 $) dans la section "AWS Budgets" pour recevoir des alertes en cas de dépassement des limites de l'offre gratuite.

### Tarification d'AWS (Pay-as-you-go)
AWS fonctionne sur un modèle de tarification **"pay as you go"** (paiement à l'usage).
* **Facturation** : Les services sont facturés en fonction de l'utilisation réelle (volume de données, temps d'utilisation, etc.). Les instances EC2, par exemple, sont souvent facturées **à la seconde**.
* **Offre Gratuite** : Elle inclut des limites d'utilisation généreuses (ex. : 750 heures d'instance EC2 par mois), permettant de faire tourner certains petits serveurs en permanence pendant un an.
* **Variation Régionale** : Les prix des services peuvent légèrement **varier selon la région** AWS choisie.
* **Outils de Gestion des Coûts** : Utilisez l'**AWS Calculateur de tarification** pour estimer vos coûts et le service **AWS Cost Explorer** pour analyser les dépenses passées.

---

## 2. Amazon RDS pour MongoDB et Amazon DocumentDB (compatible MongoDB)

Il est important de noter qu'**Amazon RDS ne propose pas de moteur MongoDB natif**. L'alternative d'AWS est **Amazon DocumentDB**.

### Amazon DocumentDB (compatible MongoDB)
DocumentDB est un service de base de données de documents entièrement géré, hautement évolutif et durable, conçu pour être **compatible avec les charges de travail MongoDB**.

* **Compatibilité API** : Il émule l'API et le protocole de MongoDB (similaire à MongoDB 4.0), permettant aux applications conçues pour MongoDB de se connecter. **Attention** : DocumentDB n'utilise pas le code source de MongoDB et ne prend pas en charge toutes les fonctionnalités des versions récentes de MongoDB.
* **Architecture Découplée** : Le **stockage et le calcul sont séparés**.
    * Le stockage est auto-réparateur et évolue automatiquement de 10 Go à 64 To.
    * La capacité de calcul peut être mise à l'échelle indépendamment.
* **Avantages Gérés** : AWS prend en charge la gestion complète, notamment le provisionnement, l'application des correctifs, la détection des pannes et les basculements automatiques vers un réplica en cas de besoin.
* **Performance** : L'architecture de stockage basée sur un flux de journaux permet d'atteindre une latence faible (quelques millisecondes) et de supporter des millions de lectures par seconde.

---

## 3. Déploiement d’une Instance MongoDB dans un Conteneur Docker sur Amazon ECS

Déployer MongoDB conteneurisé est une approche flexible, réalisable via **Amazon Elastic Container Service (ECS)**.

* **Choix de l'Infrastructure ECS** : Vous pouvez exécuter les conteneurs MongoDB sur :
    * **AWS Fargate** : Mode sans serveur qui gère l'infrastructure pour vous.
    * **Instances EC2** : Vous gérez les instances sur lesquelles les conteneurs sont exécutés.
* **Image Docker** : Utilisez l'image officielle de la **MongoDB Community Edition** ou **Enterprise Edition** de Docker Hub.
* **Persistance des Données (Cruciale)** : Contrairement aux conteneurs éphémères, une base de données doit persister. Pour cela, vous devez :
    * Utiliser des volumes de stockage, souvent **Amazon EFS** (Elastic File System), montés sur le conteneur pour assurer que les données ne sont pas perdues en cas de redémarrage ou de remplacement du conteneur.
* **Sécurité des Informations d'Identification** : Les mots de passe et autres secrets de la base de données doivent être stockés dans **AWS Secrets Manager** et injectés de manière sécurisée dans la définition de tâche ECS via des variables d'environnement.
* **Outils de Déploiement** : L'utilisation de l'**AWS Copilot CLI** simplifie grandement le déploiement d'applications conteneurisées prêtes pour la production sur ECS.

---

## 4. Configuration des Sauvegardes et Surveillance des Bases de Données sur AWS

AWS offre des services complets pour automatiser la gestion des données et des performances de vos bases de données.

### Configuration des Sauvegardes
* **AWS Backup (Service Centralisé)** : Permet de définir des **plans de sauvegarde centralisés** (politiques de rétention, fréquence) pour différents services AWS, y compris les bases de données.
* **Sauvegardes Gérées (RDS/DocumentDB)** : Pour les services gérés :
    * Les **sauvegardes automatiques** sont toujours activées.
    * Elles permettent une **restauration ponctuelle (*point-in-time recovery*)** à n'importe quel moment au cours de la période de rétention (jusqu'à 35 jours).
    * Vous pouvez également prendre des **instantanés manuels** (*snapshots*) pour une rétention à long terme ou pour un partage entre comptes.

### Surveillance des Bases de Données
* **AWS CloudWatch** : Le service de surveillance et d'observabilité standard d'AWS.
    * **Métriques** : Collecte des indicateurs de performance clés (utilisation CPU, latence des lectures/écritures, nombre de connexions) pour votre base de données.
    * **Alarmes** : Configurez des alertes pour notifier les équipes ou déclencher des actions (comme le redémarrage d'une instance) si une métrique dépasse un seuil défini.
* **AWS CloudTrail** : Enregistre l'activité des API (actions de gestion) sur votre compte, essentiel pour l'**audit** des modifications apportées à la base de données ou aux politiques de sauvegarde.
* **Surveillance Gérée** : DocumentDB inclut nativement la détection des pannes et la gestion des basculements automatiques.