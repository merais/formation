# Journal de bord de migration de la BDD vers MongoDB

### **Exercice 1 :**

### *Étape 1 :*

- Préparation du **dictionnaire de données** : `ABAI_P5_01_dico_donnees.xlsx`
- Réflexion pour la **base de données** :
  - Nom de la BDD : `healthcare_db`.
  - Nom de la table : `patients`.
- Création du script de création de la BDD et importation des données : `script_bdd.py`

### *Étape 2 :*

- Réflexion pour **Docker** :
  - Nombre de **conteneurs** : `2`
    - `mongodb` : Conteneur standard pour la base de données.
    - `migrator` : Conteneur qui exécute le script de migration Python.
  - Nombre de **volumes** : `2`
    - **Un** pour la **persistance des données** de la base de données.
    - **Un** pour le **CSV des données**.
  
### *Étape 3 :*

- Modification du script `script_bdd.py` pour prendre en compte les variables d'environnement de Docker.
- Création du `Dockerfile` pour l'importation des sources .csv et du script d'importation.
- Création du `docker-compose` pour orchestrer la mise en place du conteneur MongoDB et du conteneur d'importation des données ainsi que la création des volumes.
- Création du `.dockerignore` pour optimiser le build.

### *Étape 4 :*

- Rédaction du `README.md`
  - Présentation rapide de l'architecture.
  - Prérequis avant exécution.
  - Utilisation globale :
    - Démarrage (et fabrication si besoin) de MongoDB seul.
    - Construction du conteneur Python d'import des données.
    - Exécution de l'importation des données dans MongoDB.
    - Arrêt des services.
    - Suppression totale (avec suppression des données).
  - Les variables d'environnement utilisées.
  - L'accès à la BDD du conteneur.
  - Exemple de commandes à utiliser.
  - Dépannage.
  - Informations de sécurité.