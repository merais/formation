# README

Ce repo est destiné à mes scripts pour ma formation de Data Engineer de la platforme OpenClassroom

## Tableaux des projets

|Numéro | Nom | Date de début | Date de fin |
| :-----------------------------: | :-------------------------------------- | :----------------: | :----------------: |
|P1  | Découvrez votre formation de Data Engineer 											|   05/08/2025    |    10/08/2025   |
|P2  | Analysez les données de systèmes éducatifs 											|   10/08/2025    |    24/08/2025   |
|P3  | Entraînez-vous avec SQL et créez votre BDD 											|   24/08/2025    |    06/09/2025   |
|P4  | Auditez un environnement de données													|   06/09/2025    |    24/09/2025   |
|P5  | Maintenez et documentez un système de stockage des données sécurisé et performant 	|   24/09/2025    |    13/10/2025   |
|P6  | Anticipez les besoins en consommation de bâtiments 									|   13/10/2025    |    04/11/2025   |
|P7  | Concevez et analysez une base de données NoSQL 										|   04/11/2025    |    27/11/2025   |
|P8  | Construisez et testez une infrastructure de données 								    |   27/11/2025    |    19/12/2025   |
|P9  | Modélisez une infrastructure dans le cloud 											|   19/12/2025    |    15/01/2026   |
|P10 | Mettez en place le pipeline d'orchestration des flux 								|   15/01/2026    |    16/02/2026   |
|P11 | Catégorisez automatiquement des questions 											|   16/02/2026    |    10/03/2026   |
|P12 | Gérez un projet d'infrastructure 													|   10/03/2026    |    11/04/2026   |
|P13 | Réalisez votre portfolio de Data Engineer 											|   11/04/2026    |    04/05/2026   |
---

## Titre des dossiers par projet *(en gras celui en cours)*
- P1_Decouvrez_votre_formation_de_data_engineer_aymeric_bailleul
- P2_Analysez_les_donnees_de_systemes_educatifs_aymeric_bailleul
- P3_Entrainez-vous_avec_sql_et_creez_votre_bdd_aymeric_bailleul
- P4_Auditez_un_environnement_de_donnees_aymeric_bailleul
- P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_aymeric_bailleul
- P6_Anticipez_les_besoins_en_consommation_de_batiments_aymeric_bailleul
- P7_Concevez_et_analysez_une_base_de_donnees_nosql_aymeric_bailleul
- P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul
- P9_Modelisez_une_infrastructure_dans_le_cloud_aymeric_bailleul
- **P10_Mettez_en_place_le_pipeline_d_orchestration_des_flux_aymeric_bailleul**
- P11_Categorisez_automatiquement_des_questions_aymeric_bailleul
- P12_Gerez_un_projet_d_infrastructure_aymeric_bailleul
- P13_Realisez_votre_portfolio_de_data_engineer_aymeric_bailleul

---

## 🐍 Configuration des environnements Python par projet

Chaque projet dispose de son propre environnement virtuel Python. Voici comment sélectionner le bon interpréteur dans VS Code :

### 📋 Procédure de sélection de l'environnement

1. **Ouvrir la palette de commandes** : `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (Mac)
2. Tapez : **`Python: Select Interpreter`**
3. Choisissez l'environnement du projet actuel dans la liste
4. **OU** cliquez sur **"Enter interpreter path..."** et collez le chemin exact ci-dessous

### 🗂️ Chemins des interpréteurs Python par projet

| Projet | Version Python | Chemin de l'interpréteur |
|--------|----------------|--------------------------|
| **P2** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P2_Analysez_les_donnees_de_systemes_educatifs_bailleul_aymeric\.venv\Scripts\python.exe` |
| **P5** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P5_Maintenez_et_documentez_un_systeme_de_stockage_des_donnees_securise_et_performant_bailleul_aymeric\.venv\Scripts\python.exe` |
| **P6** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P6_Anticipez_les_besoins_en_consommation_de_batiments_bailleul_aymeric\.venv\Scripts\python.exe` |
| **P7** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P7_Concevez_et_analysez_une_base_de_donnees_nosql_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P8** | Python 3.10 | `G:\Mon Drive\_formation_over_git\P8_Construisez_et_testez_une_infrastructure_de_donnees_aymeric_bailleul\.venv\Scripts\python.exe` |
| **P9** | Python 3.14 | `G:\Mon Drive\_formation_over_git\P9_Modelisez_une_infrastructure_dans_le_cloud_aymeric_bailleul\.venv\Scripts\python.exe` |

### ✅ Vérification

Après sélection, vous devriez voir en bas à droite de VS Code :
- **Python 3.14.0 ('.venv': venv)** pour P2, P5, P6, P7, P9
- **Python 3.10.11 ('.venv': venv)** pour P8

### 🔄 En cas de problème

Si l'environnement n'apparaît pas dans la liste :
1. **Ctrl+Shift+P** → `Developer: Reload Window`
2. Réessayez la sélection de l'interpréteur

### 📦 Dépendances principales par projet

- **P2** : pandas, numpy, matplotlib, seaborn, jupyter
- **P5** : pandas, pymongo, pytest, python-dotenv
- **P6** : pandas, numpy, scikit-learn, bentoml, pydantic, jupyter
- **P7** : pymongo, polars, python-dotenv
- **P8** : airbyte, duckdb, pandas, sqlalchemy
- **P9** : python-dotenv, pytest, black, flake8

---