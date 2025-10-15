# Journal de bord de migration de la BDD vers MongoDB

### *Étape 0:*
- Création du repo `merais\formation` > Déjà fait depuis le début de la formation.
- Création du dossier contenant tout les fichiers en liens avec le porjet.
  - Permalink Github : https://github.com/merais/formation/tree/d6171005f0f5a8c23b6ca35276c0fefa61d518ad/P5_Maintenez_et_documentez_un_syst%C3%A8me_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric/_projet 
- Création du drive Google pour enregistrer tout le travail (y compris les sources et autres fichiers ignorés par le .gitignore à la racine du repo).
  - Lien GoogleDrive : https://drive.google.com/drive/folders/10Qf2RcjWwrMhN26JyQrY_CDQ1LS3bxVw?usp=sharing

### *Étape 1 :*

- Préparation du **dictionnaire de données** : `ABAI_P5_01_dico_donnees.xlsx`
- Réflexion pour la **base de données** :
  - Nom de la BDD : `healthcare_db`.
  - Nom de la table : `patients`.
- Création du script de création de la BDD, de vérification et importation des données : `local_script_bdd.py`.
- Création du script de test de la bdd : `local_test_bdd.py`.

### *Étape 2 :*

- Réflexion pour **Docker** :
  - Nombre de **conteneurs** : `2`
    - `mongodb` : Conteneur standard pour la base de données.
    - `import_scripts` : Conteneur qui exécute le script de migration Python.
  - Nombre de **volumes** : `2`
    - **Un** pour la **persistance des données** de la base de données.
    - **Un** pour le **CSV des données** et pour les **scripts python**.
  - Quelles dépendances pour les conteneurs.
  
### *Étape 3 :*

- Création du script `docker_script_bdd.py` depuis `local_script_bdd.py` pour prendre en compte les variables d'environnement de Docker.
- Création du script `docker_tests_bdd.py` depuis `local_tests_bdd.py` pour prendre en compte les variables d'environnement de Docker.
- Création du `Dockerfile` pour l'importation des sources .csv et des scripts.
- Création du `docker-compose` pour orchestrer la mise en place du conteneur `mongodb` et `import_scripts` ainsi que la création des volumes.
- Création du `.dockerignore` pour optimiser le build.
- Implémentation de la solution.

### *Étape 4 :*

- Rédaction du `local_README.md`
  - Fonctionnement des scripts.
  -  Troubleshooting.
- Rédaction du `docker_README.md`
  - Présentation rapide de l'architecture.
  - Prérequis avant exécution.
  - Utilisation globale :
    - Démarrage(et fabrication si besoin) de MongoDB seul.
    - Construction du conteneur Python d'import des données.
    - Exécution de l'importation des données dans MongoDB.
    - Arrêt des services.
    - Suppression totale (avec suppression des données).
  - Les variables d'environnement utilisées.
  - L'accès à la BDD du conteneur.
  - Exemple de commandes à utiliser.
  - Troubleshooting.
  - Informations de sécurité.