# Mission — Auditez un environnement de données

## Comment allez-vous procéder ?

Cette mission en 3 parties suit un scénario de projet professionnel.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?

**SuperSmartMarket** est une chaîne de supermarchés en plein développement en France. Cette entreprise redéfinit le concept du supermarché en intégrant des technologies de pointe pour rendre les courses rapides et agréables aux consommateurs.

L'entreprise souhaite se démarquer en mettant l'accent sur l'hyper personnalisation de l'expérience en magasin : coupons promotionnels personnalisés, recommandations basées sur les historiques d'achat, recettes personnalisées...

SuperSmartMarket a besoin d'agrandir son équipe Data en recrutant un Data Engineer pour l'aider à comprendre et analyser les différents flux de données. Vous êtes intégré à l'**équipe Data Support**, qui garantit la sécurité et la qualité des données pour l'ensemble de l'entreprise. Elle utilise une planification de processus avec des solutions Microsoft, un **entrepôt de données type OLAP** et le support de l'application **Microsoft PowerBI**.

---

# Partie 1 — Auditez l'architecture et les données de l'entreprise

## Vous recevez un mail d'Hugo (responsable du pôle Business Intelligence) :

```
De : Hugo
À : Moi
Objet : Audit de la base de données OLAP

Salut !

Je te souhaite la bienvenue dans notre équipe Data, nous sommes tous enthousiastes à l'idée de travailler avec toi.

Comme tu le sais, nous souhaitons nous démarquer par notre connaissance des clients. Mais pour le moment, nous parvenons à peine à avoir un chiffre d'affaires juste !

C'est sur ce point que je sollicite ton aide. Nous avons des incohérences dans les données que nous utilisons.

Je t'explique le problème… nos données de chiffres d'affaires ne sont pas stables dans le temps. L'historique de chiffre d'affaires a tendance à évoluer à la hausse ou à la baisse.

Je te donne un exemple : le chiffre d'affaires du lundi 14 août était de 275 186,59 €. Le lendemain, c'était le 15 août et tous nos magasins étaient fermés. Pourtant, quand nous sommes retournés sur PowerBI le 16 Août, le chiffre d'affaires du 14 août était de 284 243,88 €.

Pour te permettre de commencer ton investigation, tu peux consulter notre architecture en pièce jointe. Nous n'avons malheureusement jamais documenté notre base de données.

Pourrais-tu préparer :
- un dictionnaire des données ;
- un schéma relationnel sur la base du fichier à plat de la base de données OLAP ?

Dans un deuxième temps, peux-tu me confirmer les chiffres que je vois dans PowerBI dans ton prototype de base de données :
- le chiffre d'affaires total pour le 14 août (275 186,59 € ou 284 243,88 €) ;
- le chiffre d'affaires par client pour le top 10 des clients ;
- la part de chiffre d'affaires encaissé par employé.

Je te conseille de faire cela en mode POC (Proof Of Concept) : tu fais un prototype de base de données en local (SQLite, PostGré ou encore MySQL) et tu fais des requêtes SQL dans ta base de données pour vérifier et identifier les bons chiffres.

Pour finir, peux-tu préparer un support de présentation présentant :
- ta compréhension de l'architecture de l'entreprise ;
- le schéma relationnel que tu as créé ;
- le dictionnaire des données ;
- les résultats des requêtes ;
- ta compréhension de notre problème.

Merci beaucoup et bon courage !

Hugo
Responsable de l'équipe BI

PJ1 : Schéma de l'architecture de l'entreprise
PJ2 : Extraction à plat de la base de données OLAP
PJ3 : Template de support de présentation
```

Cette mission est entièrement guidée. Vous pouvez suivre les étapes ci-dessous.

## Étape 1 - Consolidez les notions importantes avant de démarrer cette mission

### Instructions
Révisez les notions de :
- entrepôt de données ;
- modèle en étoile.

## Étape 2 - Prenez de la hauteur sur l'architecture et la base de données

### Prérequis
- Avoir compris les principes d'un entrepôt de données OLAP et d'un modèle en étoile.
- Avoir compris les flux de données dans une base de données SQL.

### Résultats attendus
- Le dictionnaire des données
- Le schéma relationnel

### Instructions
1. Comprenez l'architecture et les flux des données de l'entreprise.
2. Examinez le fichier de données à plat afin de comprendre les données.
3. Préparez un dictionnaire des données à partir du fichier à plat.
4. Créez un schéma relationnel de la base de données.

### Recommandations
- Vous pouvez utiliser SQL Power Architect pour faire votre schéma de base de données.

## Étape 3 - Créez la base de données et des requêtes SQL

### Prérequis
- Avoir fait un dictionnaire des données.
- Avoir fait un schéma relationnel de la base de données.

### Résultats attendus
- Le fichier PPT complété.
- La base de données chargée.

### Instructions
1. Créez la base de données.
2. Chargez vos données.
3. Faites les requêtes SQL.

### Recommandations
- Vous pouvez utiliser n'importe quelle base de données (MySQL, PostgreSQL, SQLite, etc.).
- Il faut bien contrôler que l'ensemble des données soit présent dans votre base de données sans quoi votre chiffre d'affaires ne sera pas conforme.

## Étape 4 - Vérifiez votre travail et faites le point avec votre mentor

Téléchargez et complétez la fiche d'autoévaluation. Parlez-en avec votre mentor durant votre dernière session de mentorat.

---

# Partie 2 — Analysez les logs de la base de données

## Vous recevez un deuxième mail d'Hugo :

```
De : Hugo
À : Moi
Objet : Re: Audit de la base de données OLAP

Merci pour le support ! Le CA confirmé est bien de 284 243,88 €.
En pièce jointe, tu trouveras les logs de la semaine du mois d'août. Peux-tu les étudier ?

PJ: Logs.xlsx
```

## Étape 1 - Insérez les logs dans la BDD et comprenez-les

### Résultats attendus
- Création d'une nouvelle table pour les logs.
- Insertion des logs dans la base de données.
- Vérification de l'unicité et cohérence des données.

### Outils
- SQL (CREATE TABLE, INSERT INTO)

## Étape 2 - Corrigez dynamiquement la BDD avec les logs

### Résultats attendus
- Script SQL utilisant les logs pour corriger les données (INSERT, UPDATE, DELETE).
- Utilisation de jointures pour relier les logs aux tables existantes.

### Outils
- SQL avancé (jointures, sous-requêtes, transactions)

---

# Partie 3 — Faites des recommandations pour l'entreprise

## Vous recevez un troisième mail d'Hugo :

```
De : Hugo
À : Moi
Objet : Recommandations

Hugo est ravi de votre travail ! Il vous demande de préparer :
1. Un rapport d'audit
2. Un support de présentation avec cheminement + résultats
3. Des mesures correctives intégrées (triggers, contraintes, clés étrangères, propriétés ACID, procédures stockées...)
4. Un prototype intégré dans le support

PJ: Exemple de rapport d'audit
```

### Résultats attendus
- Rapport d'audit complet.
- Support de présentation incluant : cheminement, résultats, mesures correctives.
- Démonstration du prototype fonctionnel (triggers, contraintes, procédures stockées).
