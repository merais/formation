# Exercice : Conversion de documents municipaux avec Docling

## Contexte

Vous êtes chargé d'analyser un ensemble de documents municipaux numérisés, regroupés dans une archive contenant divers formats tels que PDF, Word, Excel et images.

Pour faciliter l'exploitation de ces documents, vous allez utiliser l'outil open-source Docling, qui permet de convertir efficacement ces formats en fichiers Markdown ou JSON, tout en préservant la structure et le contenu des documents originaux.

## Consignes

### 1. Installation de Docling

Assurez-vous d'avoir Python installé sur votre système. Installez Docling en exécutant la commande suivante dans votre terminal :

```bash
pip install docling
```

### 2. Documents sources

Les documents municipaux ont été téléchargés depuis le dépôt GitHub OpenClassrooms et sont disponibles dans le dossier `sources/RAW/`.

Les documents sont organisés par catégories :
- **budget/** : Documents budgétaires
- **communication/** : Documents de communication
- **demandes citoyennes/** : Demandes des citoyens
- **evenements/** : Documents relatifs aux événements
- **instances/** : Documents des instances municipales
- **projets/** : Documents de projets

### 3. Conversion des documents

Utilisez le script Python `convert_documents.py` fourni pour convertir tous les documents du répertoire `sources/RAW/` en fichiers Markdown.

Le script :
- Parcourt récursivement tous les sous-dossiers
- Détecte automatiquement le format de chaque fichier
- Effectue la conversion appropriée en utilisant Docling
- Sauvegarde les résultats dans le dossier `convert/`

## Structure du projet

```
exercice_docling/
├── README.md                    # Ce fichier
├── convert_documents.py         # Script de conversion
├── requirements.txt             # Dépendances Python
└── sources/
    ├── RAW/                     # Documents sources téléchargés depuis GitHub
    │   ├── budget/
    │   ├── communication/
    │   ├── demandes citoyennes/
    │   ├── evenements/
    │   ├── instances/
    │   └── projets/
    └── convert/                 # Les fichiers Markdown générés
```

## Utilisation

1. Installez Docling :

```bash
pip install docling
```

2. Les documents sources sont déjà présents dans `sources/RAW/`

3. Exécutez le script :

```bash
python convert_documents.py
```

4. Les fichiers Markdown seront générés dans le dossier `sources/convert/`

## Exercice 2 : Similarité et visualisation des embeddings

### Objectif

Comparer plusieurs textes du corpus municipal avec trois approches d'embeddings
(Mistral, Sentence-BERT, FastText) et visualiser leur distribution en 2D.

### Pré-requis

1. Avoir déjà converti les documents (voir l'exercice 1)
2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

3. (Optionnel) Configurer la clé Mistral pour l'API d'embeddings :

```bash
setx MISTRAL_API_KEY "votre_cle"
```

### Lancer l'exercice

```bash
python compare_embeddings.py --max-docs 10
```

### Résultats

Le script génère dans `outputs/` :

- `similarity_<modele>.csv` : matrice de similarité cosinus
- `embeddings_<modele>.png` : visualisation PCA en 2D

## Formats supportés

- PDF
- Word (.docx, .doc)
- Excel (.xlsx, .xls)
- Images (JPG, PNG, etc.)
