# Documentation : Fonctionnement des scripts local

## Fonctionnement du script `local_script_bdd.py`

Le script `local_script_bdd.py` est conçu pour :
1. Nettoyer les données d'un fichier CSV.
2. Ajouter un identifiant unique `id_patient` à chaque enregistrement.
3. Importer les données nettoyées dans une base de données MongoDB locale.

## Étapes principales du script

### 1. Connexion à MongoDB
- Le script utilise la bibliothèque `pymongo` pour se connecter à une base de données MongoDB locale.
- Les paramètres de connexion sont définis dans le script :
  - `DB_NAME` : Nom de la base de données (par défaut : `healthcare_db`).
  - `URI` : URI de connexion MongoDB (par défaut : `mongodb://localhost:27017/`).
  - `COLLECTION_NAME` : Nom de la collection (par défaut : `patients`).

### 2. Nettoyage des données
- Le fichier CSV source est défini par la variable `SOURCE_CSV` (par défaut : `./sources/healthcare_dataset.csv`).
- Le script effectue les opérations suivantes :
  - Conversion des colonnes de dates (`Date of Admission`, `Discharge Date`) en format datetime.
  - Suppression des doublons.
  - Gestion des valeurs manquantes.
  - Ajout d'un champ unique `id_patient` pour chaque enregistrement.
  - Sauvegarde des données nettoyées dans un nouveau fichier CSV avec le suffixe `_cleaned`.

### 3. Importation des données dans MongoDB
- Les données nettoyées sont lues depuis le fichier CSV nettoyé.
- Chaque enregistrement est converti en dictionnaire avant d'être inséré dans la collection MongoDB spécifiée.
- Le champ `id_patient` est utilisé comme identifiant unique pour chaque document.

## Prérequis
- MongoDB doit être en cours d'exécution localement.
- Le fichier CSV source doit exister dans le chemin spécifié par `SOURCE_CSV`.
- Les dépendances Python nécessaires (`pandas`, `pymongo`) doivent être installées via `requirements.txt` :
  ```bash
  pip install -r requirements.txt
  ```

## Commande pour exécuter le script
```bash
python local_script_bdd.py
```

## Résultats
- Les données nettoyées sont sauvegardées dans un fichier CSV avec le suffixe `_cleaned`.
- Les données sont insérées dans la base de données MongoDB locale avec un champ `id_patient` unique.

## Dépannage
- **Erreur de connexion à MongoDB** : Vérifiez que MongoDB est en cours d'exécution et que l'URI est correct.
- **Fichier CSV introuvable** : Assurez-vous que le fichier existe dans le chemin spécifié par `SOURCE_CSV`.
- **Dépendances manquantes** : Installez les dépendances avec `pip install -r requirements.txt`.

## Exemple de structure de document dans MongoDB
```json
{
  "id_patient": "12345",
  "Nom": "Dupont",
  "Date of Admission": "2025-01-01",
  "Discharge Date": "2025-01-10",
  "Medical Condition": "Hypertension"
}
```

---

## Fonctionnement du script `local_tests_bdd.py`

Le script `local_tests_bdd.py` est conçu pour effectuer des tests sur la base de données MongoDB locale afin de vérifier l'intégrité et la validité des données insérées. Voici les principales fonctionnalités :

### 1. Connexion à MongoDB
- Le script se connecte à la base de données MongoDB locale en utilisant les mêmes paramètres que `local_script_bdd.py` :
  - `DB_NAME` : Nom de la base de données (par défaut : `healthcare_db`).
  - `URI` : URI de connexion MongoDB (par défaut : `mongodb://localhost:27017/`).
  - `COLLECTION_NAME` : Nom de la collection (par défaut : `patients`).

### 2. Tests effectués
- **Vérification du nombre de documents** :
  - Compte le nombre total de documents dans la collection MongoDB.
  - Compare ce nombre avec le nombre attendu (par exemple, le nombre de lignes dans le fichier CSV nettoyé).

- **Vérification des doublons** :
  - Vérifie qu'il n'y a pas de doublons dans la collection MongoDB (basé sur le champ `id_patient`).

- **Vérification des champs obligatoires** :
  - Vérifie que tous les documents contiennent les champs obligatoires (`id_patient`, `Nom`, `Date of Admission`, etc.).

- **Exemple de requêtes MongoDB** :
  - Recherche un document spécifique par `id_patient`.
  - Affiche les 5 premiers documents pour inspection.

### 3. Résultats des tests
- Les résultats des tests sont affichés dans la console pour permettre une analyse rapide.
- En cas d'erreur, le script affiche des messages détaillés pour faciliter le dépannage.

## Commande pour exécuter le script
```bash
python local_tests_bdd.py
```

## Dépannage
- **Erreur de connexion à MongoDB** : Vérifiez que MongoDB est en cours d'exécution et que l'URI est correct.
- **Données manquantes ou incorrectes** : Vérifiez que les données ont été correctement insérées par `local_script_bdd.py`.

## Exemple de sortie
```plaintext
Connexion à MongoDB réussie.
Nombre total de documents : 100
Aucun doublon détecté.
Tous les champs obligatoires sont présents.
Exemple de document :
{
  "id_patient": "12345",
  "Nom": "Dupont",
  "Date of Admission": "2025-01-01",
  "Discharge Date": "2025-01-10",
  "Medical Condition": "Hypertension"
}
```