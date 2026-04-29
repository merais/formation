# Exercice — Modélisez une infrastructure dans le cloud

## Comment allez-vous procéder ?

Ce projet se compose de deux exercices indépendants.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

---

## Exercice 1 — Infrastructure hybride pour InduTechData

**Contexte :** Vous intervenez comme consultant Data Engineer pour **InduTechData**, entreprise de 15 ans spécialisée dans l'IoT industriel. Le volume de données dépasse désormais +50 Go/mois et le datacenter on-premise atteint ses limites.

**SI existant :**
- SQL Server (40 To, ERP + CRM)
- SAN (10 To, données non structurées)
- Active Directory
- Serveurs ERP + CRM

### Étape 1 - Identifiez les composants cloud pour l'architecture hybride

#### Résultats attendus
- Sélection justifiée de chaque composant cloud :
  - Stockage non structuré → service de stockage objet cloud (ex. S3)
  - Entrepôt de données → entrepôt SQL cloud (ex. Redshift, BigQuery, Synapse)
  - Streaming IoT → **Redpanda** (compatible Kafka, faible consommation énergétique)
  - Sécurité / SSO → extension cloud d'Active Directory

#### Points de vigilance
- Les flux critiques doivent rester accessibles même en cas d'indisponibilité partielle du cloud.
- Les accès doivent être sécurisés (SSL/TLS pour Redpanda, IAM pour le cloud).
- Anticiper les coûts cloud (calcul, stockage, transfert).

### Étape 2 - Représentez visuellement l'architecture

#### Résultats attendus
- Schéma d'architecture hybride (on-premise ↔ cloud) sous forme de diagramme (Lucidchart, Draw.io).
- Export en PDF ou PNG.

### Étape 3 - Évaluez la compatibilité avec le SI existant

#### Résultats attendus
- Document Word de 400 à 1 200 mots couvrant :
  - Sécurité (ex. SSL/TLS Redpanda, chiffrement au repos)
  - Interopérabilité (Redpanda ↔ SQL Server, connecteurs JDBC/ODBC)
  - Scalabilité et estimation des coûts (AWS Pricing Calculator, CloudWatch)
  - Avantages, limitations et points d'attention

---

## Exercice 2 — Gestion de tickets clients avec Redpanda et PySpark

**Contexte :** InduTechData souhaite migrer son système de gestion des tickets clients vers AWS, avec un traitement en temps réel. Vous devez réaliser un POC.

**Structure des tickets :**
- ID ticket, ID client, date/heure, demande, type de demande, priorité

### Étape 1 - Configurez Redpanda

#### Résultats attendus
- Topic `client_tickets` créé dans Redpanda.
- Script Python producteur de tickets simulés.

#### Outils
- Python 3, bibliothèques Redpanda / Kafka, éventuellement MySQL pour les données sources.

### Étape 2 - Traitez les données avec PySpark

#### Résultats attendus
- Script PySpark qui consomme le topic `client_tickets` et applique des transformations.

### Étape 3 - Exportez les données

#### Résultats attendus
- Export des données transformées en JSON, Parquet ou autre format adapté.

### Étape 4 - Conteneurisez l'application

#### Résultats attendus
- `Dockerfile` et `docker-compose.yml` permettant de lancer l'ensemble du POC.
- Répertoire zippé contenant le code complet.

### Étape 5 - Documentez et présentez

#### Résultats attendus
- `README.md` décrivant l'installation et l'utilisation.
- Diagramme Mermaid représentant le flux de données.
- Vidéo de démonstration (Loom ou YouTube non listé).
