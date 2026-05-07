# Projet 11 — Concevez et déployez un système RAG

**Évaluation :** lundi 2 mars 2026
**Statut :** Projet validé

---

## Remarques sur l'évaluation

Dans ce projet, Aymeric devait développer un **Proof of Concept (POC)** pour un système de recommandation d'événements culturels basé sur un **chatbot intelligent**. L'objectif était d'intégrer des données d'événements provenant de l'API **Open Agenda**, de les transformer en vecteurs sémantiques à l'aide du modèle **Mistral**, puis de les indexer dans une base vectorielle **Faiss** afin de permettre une recherche sémantique efficace.

Le système devait ensuite être orchestré avec **LangChain**, qui permet de relier la base vectorielle et le modèle de langage afin de construire une architecture de type **RAG (Retrieval Augmented Generation)**. Cette architecture permet au chatbot de générer des réponses pertinentes en s'appuyant sur les données stockées dans la base vectorielle.

Le projet avait pour objectif de valider plusieurs compétences avancées en data engineering et en intelligence artificielle appliquée, notamment la gestion de bases vectorielles, l'intégration de modèles NLP et la conception d'une chaîne de traitement intelligente.

---

**Compétences évaluées**

---

**1. Identifier ou créer un modèle d'apprentissage adapté aux contraintes et besoins métiers**

Validé

Commentaires :

Aymeric a sélectionné une architecture pertinente reposant sur un système **RAG** combinant un modèle de génération de texte et une base de connaissances vectorielle. Le choix du modèle **Mistral** pour la génération de vecteurs et de réponses est adapté aux besoins du projet.

L'intégration avec **LangChain** permet d'orchestrer efficacement les interactions entre le modèle de langage et la base vectorielle **Faiss**. Cette architecture permet au chatbot d'exploiter les données indexées pour générer des réponses contextualisées et pertinentes.

L'étudiant a également su expliquer l'architecture globale du système ainsi que le rôle de chaque composant dans le fonctionnement du chatbot. Les réponses générées par le système sont cohérentes avec les données disponibles dans la base.

---

**2. Mettre en place un processus de nettoyage afin d'améliorer la qualité des données**

Validé

Commentaires :

Aymeric a correctement mis en place un processus de préparation et de nettoyage des données provenant de l'API Open Agenda. Les données ont été structurées et enrichies afin de garantir une indexation efficace dans la base vectorielle.

Le processus inclut notamment l'analyse des données récupérées, leur nettoyage, l'ajout de métadonnées pertinentes et la fragmentation des contenus textuels afin d'optimiser la génération de vecteurs sémantiques. Cette approche permet d'améliorer la qualité des résultats obtenus lors des recherches vectorielles.

Les différentes étapes de transformation sont documentées et les scripts permettent de reproduire le pipeline de préparation des données.

---

**3. Configurer l'environnement de travail nécessaire à l'exploitation des données**

Validé

Commentaires :

Aymeric a mis en place un environnement de travail adapté aux exigences du projet. L'architecture technique proposée repose sur une combinaison cohérente d'outils spécialisés, notamment **LangChain pour l'orchestration**, **Faiss pour la recherche vectorielle** et **Mistral pour la génération des vecteurs et des réponses**.

L'environnement permet d'exécuter les différentes étapes du pipeline de manière fluide, depuis l'extraction des données jusqu'à la génération des réponses. La configuration des dépendances et l'organisation du projet rendent la solution reproductible.

Les performances globales du système sont satisfaisantes pour un Proof of Concept et démontrent que l'architecture choisie est pertinente pour ce type d'application.

---

**Livrable**

Points forts :
- Architecture RAG bien comprise et correctement implémentée
- Intégration cohérente de LangChain, Faiss et Mistral
- Bonne structuration du pipeline de traitement des données
- Solution fonctionnelle permettant la recherche d'événements et la génération de réponses
- Documentation claire et organisation du projet cohérente
- Bonne compréhension globale du fonctionnement du système

Axes d'amélioration :
- Approfondir l'optimisation des performances de l'indexation vectorielle
- Enrichir les tests unitaires pour couvrir davantage de scénarios d'utilisation
- Approfondir les stratégies de gestion de grands volumes de données vectorielles
- Documenter davantage les limites du système dans certains cas d'interrogation complexes

---

**Soutenance**

Remarques :

La soutenance s'est très bien déroulée. Aymeric a présenté son projet de manière claire, structurée et pédagogique. Il a su expliquer l'architecture du système ainsi que les choix techniques réalisés pour la mise en place du chatbot.

Les réponses apportées aux questions ont démontré une bonne compréhension des concepts liés aux bases vectorielles, aux modèles NLP et aux architectures RAG. L'étudiant a su justifier ses choix et expliquer le fonctionnement global de la solution développée.
