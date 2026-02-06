# Livrables et soutenance

## Livrables

Voici un rappel des documents que vous devez déposer sur la plateforme.

### Compétences et livrables associés

| Compétences | Livrables |
|-------------|-----------|
| **Configurer l'environnement de travail nécessaire à l'exploitation des données** | - Fichier Readme : présentation, objectifs, instructions pour la reproduction, description des fichiers/dossiers<br>- Gestion des dépendances (conda ou pip) |
| **Mettre en place un processus de nettoyage afin d'améliorer la qualité des données** | - Scripts de pré-processing et documentation intégrée sous forme de docstrings<br>- Scripts de vectorisation et création/gestion d'index vectoriels<br>- Tests unitaires intégrés sous forme de pipeline |
| **Identifier ou créer un modèle d'apprentissage adapté aux contraintes et aux besoins métiers** | - Rapport technique<br>- Code du système RAG |

### Format de dépôt

Déposez sur la plateforme, dans un dossier zip nommé `Titre_du_projet_nom_prenom`, tous les livrables du projet comme suit : `Nom_Prenom_n°_du_livrable_nom_du_livrable_date_de_démarrage_du_projet`.

Cela donnera :
- `Nom_Prenom_1_readme_012025`
- `Nom_Prenom_2_gestion_012025`
- `Nom_Prenom_3_scripts_012025`

**Exemple :** le premier livrable peut être `Janek_Meriem_1_readme_012025`

---

## Soutenance

**La soutenance ne porte que sur la mission.**

Durant la présentation orale, l'évaluateur interprétera le rôle de Jérémy. La soutenance dure **30 minutes** et sera structurée de la manière suivante :

### 1. Présentation des livrables (15 minutes)
- Présentation du système, justification technique des briques mises en place
- Démonstration du système depuis l'environnement local

### 2. Discussion (10 minutes)
L'évaluateur jouera le rôle de Jérémy. Il vous challengera sur les points suivants :
- Peux-tu expliquer comment Faiss optimise les recherches dans une base vectorielle ?
- Quelles seraient les limitations de Faiss pour une grande quantité de données ?
- Pourquoi choisir LangChain pour intégrer des modèles NLP dans un pipeline ?
- Quelles méthodes utilises-tu pour garantir la qualité des données dans un pipeline automatisé ?
- Comment détecter les dérives de performance dans un modèle déployé ?
- Quels indicateurs de performance sont les plus importants pour suivre un modèle en production ?

### 3. Débrief (5 minutes)
À la fin de la soutenance, l'évaluateur arrêtera de jouer le rôle de Jérémy pour vous permettre de débriefer ensemble.

---

### Durée de présentation

Votre présentation doit durer **15 minutes** (+/- 5 minutes). 

Puisque le respect des durées des présentations est important en milieu professionnel, les présentations en dessous de 10 minutes ou au-dessus de 20 minutes peuvent être refusées.
