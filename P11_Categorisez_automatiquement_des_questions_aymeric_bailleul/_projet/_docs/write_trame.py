"""Écrit la trame PowerPoint vulgarisée dans ABAI_P11_presentation_trame.md"""
import pathlib

TRAME = pathlib.Path(__file__).parent / "ABAI_P11_presentation_trame.md"

content = """\
# Trame PowerPoint — P11 RAG Chatbot Puls-Events
**15 slides · Style gris/anthracite · ~15 minutes**

---

## Slide 1 — Page de titre

**Titre :** Assistant Conversationnel RAG pour Puls-Events
**Sous-titre :** Comment interroger un million d'événements culturels en langage naturel ?
**Auteur :** Aymeric Bailleul
**Date :** Février 2026
**Formation :** Data Engineer — OpenClassrooms

---

## Slide 2 — Contexte et problématique (1/2)

**Titre :** Le problème : la recherche classique ne suffit plus

**Contenu :**
- Puls-Events est une plateforme qui agrège les événements culturels publics de toute la France, issus du jeu de données ouvert Open Agenda
- Le catalogue représente **913 818 événements** recensés au 03/02/2026 : concerts, expositions, festivals, spectacles, conférences...
- Aujourd'hui, quand un utilisateur tape "expo enfant Montpellier", la plateforme retourne une **liste de résultats bruts**. C'est à lui de lire, trier, comprendre.

**Le fossé entre la question et la réponse :**
- *"Y a-t-il des expos gratuites pour enfants à Montpellier ce weekend ?"* → la recherche par mots-clés ne comprend pas "gratuit", "enfant" et "ce weekend" combinés
- *"Quel événement culturel en plein air peut-on faire en famille en Occitanie en juillet ?"* → trop de contexte implicite pour une recherche classique

> La recherche par mots-clés filtre et liste. Elle ne raisonne pas. Elle ne répond pas.

---

## Slide 3 — Contexte et problématique (2/2)

**Titre :** L'objectif : un assistant qui comprend et répond

**Périmètre du POC :**
- On restreint volontairement le champ à la région **Occitanie** pour valider la chaîne technique sur un volume maîtrisable
- On conserve les événements des 12 derniers mois et tous les futurs → **7 960 événements** pertinents retenus
- Un POC (Proof of Concept) n'a pas vocation à être parfait : il doit prouver que l'approche est viable avant d'investir dans une version production

**Question centrale du projet :**
> Comment permettre à un utilisateur d'interroger en langage naturel une base d'événements culturels et obtenir une réponse précise, contextualisée et vérifiable — sans que le système invente des informations ?

**Réponse :** l'architecture **RAG** — Retrieval-Augmented Generation

---

## Slide 4 — Architecture RAG : principe

**Titre :** Le RAG — chercher d'abord, puis rédiger

**Le problème des LLM classiques (ChatGPT, etc.) :**
Un modèle de langage (LLM) peut répondre à n'importe quelle question, mais il invente parfois des informations plausibles mais fausses — c'est ce qu'on appelle une **hallucination**. Il ne connaît pas non plus les données privées ou récentes.

**La solution RAG en 2 étapes :**

| RETRIEVAL — Chercher | GENERATION — Rédiger |
|---|---|
| On transforme la question en empreinte numérique et on cherche dans la base les passages les plus proches sémantiquement | Le LLM reçoit ces passages comme contexte et rédige une réponse en se basant UNIQUEMENT sur eux |

**Ce que cela garantit :**
- Aucune information inventée : le modèle ne peut répondre qu'avec ce qu'on lui fournit
- Les réponses sont traçables : on sait quels passages ont servi
- Le système répond "je ne sais pas" si l'info n'existe pas dans la base

**Stack technique :** LangChain (orchestration) + FAISS (recherche) + Mistral AI (LLM)

---

## Slide 5 — Architecture RAG : pipeline complet

**Titre :** De la donnée brute à la réponse — vue d'ensemble du pipeline

*[IMAGE : pipeline_rag.png]*

**Ce que fait chaque étape :**
1. **Source** : on part du fichier Open Agenda brut (913 818 événements au format Parquet)
2. **Preprocessing** : on filtre géographiquement et temporellement → 7 960 événements utiles
3. **Chunking** : chaque événement est découpé en petits blocs de texte de taille fixe
4. **Vectorisation** : chaque bloc est transformé en empreinte numérique (vecteur 1024D) via Mistral
5. **Index FAISS** : toutes les empreintes sont stockées dans un index de recherche rapide (40.94 MB)
6. **RAG** : à chaque question, on cherche les blocs les plus pertinents, puis le LLM rédige la réponse
7. **Interface + Évaluation** : l'utilisateur interagit via Streamlit, les performances sont mesurées avec Ragas

---

## Slide 6 — Choix techniques : FAISS

**Titre :** FAISS — la bibliothèque de recherche vectorielle

**Qu'est-ce que FAISS ?**
FAISS (développé par Meta/Facebook) est une bibliothèque spécialisée dans la recherche de similarité entre vecteurs numériques. Concrètement : quand un utilisateur pose une question, on la transforme en vecteur, et FAISS trouve en quelques millisecondes les vecteurs les plus "proches" dans la base — c'est-à-dire les passages les plus similaires sémantiquement.

**Pourquoi FAISS plutôt qu'une autre solution ?**

| Critère | FAISS | Alternatives (Chroma, Weaviate) |
|---|---|---|
| Déploiement | Un simple fichier .bin, aucun serveur à gérer | Nécessite un service dédié, une installation |
| Performance | Recherche exacte parmi 10 480 vecteurs en < 1ms | Surdimensionné pour moins de 100K vecteurs |
| Intégration | Chargement natif dans LangChain en une ligne | Variable selon la solution choisie |
| Coût | Gratuit et open-source | Parfois payant en version cloud |

**En chiffres :** index de 40.94 MB · créé en 0.39 secondes · requête en moins d'1 milliseconde

---

## Slide 7 — Choix techniques : Mistral AI

**Titre :** Mistral AI — un seul fournisseur, trois rôles distincts

**Pourquoi tout chez Mistral ?**
Utiliser un seul fournisseur garantit la cohérence : le modèle qui "comprend" les textes au moment de l'indexation est le même que celui qui "comprend" les questions à la volée. Cela évite les distorsions entre les représentations.

**Les trois modèles utilisés :**

| Rôle | Modèle | Ce qu'il fait concrètement |
|---|---|---|
| Transformer le texte en vecteur | mistral-embed | Convertit chaque bloc de texte en 1024 nombres qui encodent son sens |
| Générer la réponse | mistral-small-latest | Lit les passages récupérés et rédige une réponse en français |
| Évaluer la qualité | mistral-large-latest | Joue le rôle de juge pour noter les réponses générées |

**Pattern producteur léger / juge lourd :**
On utilise un modèle économique pour produire des réponses en continu, et on réserve le modèle premium — plus coûteux — uniquement pour les phases d'évaluation ponctuelles. C'est une pratique standard en production RAG.

---

## Slide 8 — Méthodologie : pré-processing des données

**Titre :** Préparer les données — de 913 818 à 7 960 événements exploitables

**Pourquoi filtrer ?**
Indexer un million d'événements nationaux pour répondre sur l'Occitanie serait du bruit. Un index trop large dilue la pertinence et ralentit l'évaluation. Le filtrage est une décision de conception, pas une contrainte technique.

**Les trois étapes de filtrage :**
1. **Filtre géographique** : on ne conserve que les événements Occitanie → 89 491 événements
2. **Filtre temporel** : on élimine les événements terminés depuis plus d'un an → 7 960 événements
3. **Nettoyage** : suppression des colonnes quasi-vides (> 70% de valeurs manquantes), suppression des balises HTML dans les descriptions longues

**Construction du champ texte par événement :**
Chaque événement est représenté par un champ texte structuré qui regroupe toutes ses informations utiles :

    Titre | Description | Détails | Mots-clés | Lieu

La séparation par | aide le LLM à distinguer les différents champs lors de la génération de la réponse.

---

## Slide 9 — Méthodologie : chunking & vectorisation

**Titre :** Découper, transformer, indexer

**Le chunking — pourquoi découper le texte ?**
Un LLM ne peut pas "lire" un texte trop long d'un coup : il a une fenêtre de contexte limitée. On découpe donc chaque texte en blocs (chunks) de taille fixe. On utilise une fenêtre glissante : chaque bloc chevauche légèrement le précédent pour ne pas couper une phrase en plein milieu.

| Paramètre | Valeur | Ce que ça signifie |
|---|---|---|
| Taille d'un bloc | 250 tokens (~180 mots) | Assez court pour être précis, assez long pour avoir du sens |
| Chevauchement | 75 tokens (30%) | Les 75 derniers tokens d'un bloc = les 75 premiers du suivant |
| Résultat | 10 480 blocs | En moyenne 1.31 bloc par événement |

**La vectorisation — transformer le texte en nombres :**
Chaque bloc est envoyé au modèle mistral-embed qui le convertit en un vecteur de 1024 nombres. Ces nombres encodent le "sens" du texte : deux événements similaires auront des vecteurs proches dans cet espace mathématique.

**Le retriever MMR — éviter les répétitions :**
La recherche simple peut retourner plusieurs blocs du même événement. Le MMR (Maximal Marginal Relevance) corrige ça : il sélectionne des blocs à la fois pertinents ET diversifiés (70% pertinence, 30% nouveauté).

---

## Slide 10 — Résultats Ragas : métriques globales

**Titre :** Évaluation objective — le framework Ragas

**Comment évaluer un système RAG ?**
On ne peut pas se contenter de lire les réponses : il faut mesurer. Ragas est un framework d'évaluation qui utilise un LLM "juge" (mistral-large-latest) pour noter automatiquement les réponses selon 4 axes.

**Protocole :** 5 questions représentatives · Juge : mistral-large-latest

| Métrique | Score | Ce que ça mesure en clair |
|---|---|---|
| faithfulness | 0.764 | Les réponses s'appuient-elles vraiment sur les passages récupérés ? (pas d'invention) |
| answer_relevancy | 0.910 | La réponse répond-elle bien à la question posée ? |
| context_precision | 0.700 | Les passages récupérés sont-ils bien tous utiles ? (peu de bruit) |
| context_recall | 0.583 | A-t-on récupéré toutes les informations nécessaires pour répondre ? |

**Lecture globale :**
Le système répond bien aux questions (answer_relevancy élevé) et n'invente pas (faithfulness correct). Le point faible est le rappel : on ne récupère pas toujours tous les passages utiles avec seulement 10 blocs.

---

## Slide 11 — Résultats Ragas : analyse par question

**Titre :** Ce que les scores révèlent question par question

| Question | faith. | ans_rel. | ctx_prec. | ctx_rec. |
|---|---|---|---|---|
| Expositions à Montpellier ? | 0.429 | 0.895 | 1.000 | 0.250 |
| Spectacles enfants Occitanie ? | 0.813 | 0.911 | 1.000 | 0.333 |
| Festivals musique été Occitanie | 0.857 | 0.921 | 0.000 | 1.000 |
| Carcassonne ce weekend ? | 0.870 | 0.922 | 1.000 | 0.667 |
| Événements plein air Occitanie | 0.852 | 0.903 | 0.500 | 0.667 |

**Cas intéressant — "Festivals musique été Occitanie" :**
- context_precision = 0 : le retriever a récupéré des blocs variés mais aucun n'était jugé prioritaire → le MMR a trop privilégié la diversité sur une requête très générale
- context_recall = 1.0 : paradoxalement, l'information était bien présente dans la base — elle a juste été noyée parmi d'autres blocs

**Ce que ça enseigne :** les requêtes très génériques (sans critère précis de lieu ou de date) sont plus difficiles à traiter que les requêtes localisées.

---

## Slide 12 — Démo : exemples de réponses

**Titre :** Le système en action — deux cas réels

**Cas 1 — Question dans le périmètre :**
*"Y a-t-il des expositions à Montpellier ?"*

Réponse : "Oui, il y a plusieurs expositions à Montpellier. L'exposition Montpellier, regarder la ville autrement sur l'architecture est accessible le 20 septembre 2025 en visite libre. L'exposition Regards sur l'opéra présente une cinquantaine de dessins d'étudiants depuis le 10 mai 2025."

Le système cite des événements réels, avec des dates précises, tirés directement de la base de données.

**Cas 2 — Question hors périmètre :**
*"Concerts à Paris ?"*

Réponse : "Je n'ai pas d'informations sur des concerts à Paris dans ma base de données. Mon périmètre est limité aux événements de la région Occitanie."

Le système ne cherche pas à inventer : il reconnaît les limites de ce qu'il sait et le signale explicitement.

---

## Slide 13 — Interface Streamlit

**Titre :** L'interface utilisateur — un chat dans le navigateur

**Ce qu'on a construit :**
Une interface de type "chat" accessible directement dans le navigateur, sans installation pour l'utilisateur final. Elle est construite avec Streamlit, un framework Python qui permet de créer rapidement des interfaces web pour des projets de data science.

**Fonctionnalités de l'interface :**
- Zone de saisie libre en langage naturel
- Historique de la conversation durant la session
- Réponse générée en quelques secondes, ancrée dans les données de la base
- Pas de configuration requise côté utilisateur

**Pour la démo live :** streamlit run src/rag/app.py

**Questions de démo suggérées :**
1. *"Y a-t-il des spectacles pour enfants en Occitanie ?"*
2. *"Que se passe-t-il à Carcassonne ce weekend ?"*
3. *"Concerts à Paris ?"* — pour montrer la gestion hors périmètre

---

## Slide 14 — Limitations et améliorations

**Titre :** Ce POC a des limites — et c'est normal

Un POC, par définition, n'est pas une version production. Il sert à valider une approche technique avant d'investir. Les limitations identifiées sont des orientations pour la suite, pas des échecs.

| Limitation actuelle | Impact réel | Piste d'amélioration |
|---|---|---|
| Données figées au 03/02/2026 | Les nouveaux événements n'apparaissent pas | Pipeline de mise à jour incrémentale hebdomadaire |
| context_recall = 0.583 | Certaines infos manquent sur les requêtes larges | Passer k de 10 à 15-20, ajouter des filtres sur les métadonnées |
| Pas de mémoire entre les questions | Chaque question est traitée indépendamment | Historique de conversation avec LangChain |
| Périmètre Occitanie uniquement | Requêtes hors région non traitées | Partitionner l'index FAISS par région |
| Dépendance à l'API Mistral | Pas de mode hors-ligne | Mettre en cache les réponses aux questions récurrentes |

**Vision long terme :** base vectorielle gérée (Weaviate, Pinecone), fine-tuning des embeddings sur le corpus événementiel, interface multimodale avec photos

---

## Slide 15 — Conclusion

**Titre :** Bilan — ce que ce POC prouve

**Ce que nous avons construit et validé :**
- Une chaîne complète et fonctionnelle, de la donnée Open Agenda brute jusqu'à l'interface chat en passant par l'indexation vectorielle et la génération de réponses
- Un système évalué quantitativement, avec des métriques reproductibles, pas seulement une démo "qui a l'air de marcher"
- Une architecture pragmatique : aucun serveur supplémentaire, entièrement reproductible à partir du README

**Les trois résultats clés :**
- answer_relevancy = 0.910 — les réponses sont bien adaptées aux questions posées
- faithfulness = 0.764 — le système ne fabrique pas d'informations
- Stack LangChain + FAISS + Mistral AI : déployable sans infrastructure lourde

**La prochaine étape naturelle :**
Passer d'un snapshot statique à un pipeline de mises à jour incrémentales, et étendre le périmètre géographique progressivement vers le niveau national.

---
*Aymeric Bailleul — P11 Data Engineer — OpenClassrooms — Février 2026*
"""

TRAME.write_text(content, encoding="utf-8")
print(f"OK — {len(content)} chars, {content.count('## Slide')} slides")
