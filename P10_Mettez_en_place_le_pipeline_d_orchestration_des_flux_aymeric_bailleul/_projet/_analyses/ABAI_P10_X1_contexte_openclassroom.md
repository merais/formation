Voici le contexte et le contenu complet de l'exercice :

# Mission - Construisez et testez une automatisation de transformation et analyse de données

## Comment allez-vous procéder ? 
Cette mission suit un scénario de projet professionnel. 
Vous pouvez suivre les étapes pour vous aider à réaliser vos livrables.

Avant de démarrer, nous vous conseillons de :
- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ; 
- préparer une liste de questions pour votre première session de mentorat.

## Prêt à mener la mission ?
Vous avez été récemment embauché comme Data Engineer dans l’entreprise BottleNeck, un marchand de vin prestigieux. 

Laurent, votre manager sur cette mission, vous accueille chaleureusement et vous propose de partager un café avec le reste de l’équipe. L’ambiance est bonne, et vous voilà déjà parfaitement intégré dans cette équipe détendue mais professionnelle. Vous rencontrez les responsables de produits : 
  - Laure, qui s'occupe des clients entreprises et des vins premium, 
  - Maria, qui s’occupe des particuliers et des vins ordinaires.
 
Après les présentations, effectuées dans une ambiance conviviale, Laurent vous explique le contexte data de l’entreprise : 

”Stéphane, notre data analyst a travaillé sur une première analyse de nos données. Il a présenté ses résultats lors de notre dernière réunion de COPIL et on a eu de bons retours de la part de nos responsables produits. 

Stéphane a travaillé sur ces 3 axes :  
  - Nettoyage des données provenant des 2 systèmes CMS et ERP.
  - Réconciliation de ces données afin de calculer le chiffre par produit et le chiffre d’affaires total réalisé.
  - Identification des vins premium avec utilisation des méthodes statistiques tel que le z-score et l’intervalle interquartile.

Ton rôle en tant que Data Engineer sera d’automatiser cette chaîne de traitement et d’analyse de données. 
Les responsables de données doivent recevoir les rapports des chiffres d’affaires tous les mois ainsi que les extractions des fichiers contenant les vins premium et les vins ordinaires. “

Fidèle à son habitude lors de l'arrivée d’un nouveau collaborateur, Laurent vous accompagne à votre poste de travail.
Il va vous faire suivre:
  - les données brutes par mail ; 
  - la méthode utilisée par Stéphane pour identifier les vins premium.
 
## Vous recevez le mail de Laurent:

De : Laurent
À : moi
Objet : Exports tables et démarche de Stéphane

Re,
Tu trouveras ci-joints dans le fichier zip, les 2 exports du système ERP (erp.xlsx) et de la plateforme de vente en ligne CMS (web.xlsx) et le fichier liaison. Pour réconcilier les données, il faut passer par le fichier liaison (liaison.xlsx). 

Je te laisse prendre connaissance de ces éléments.

Voici la démarche de Stéphane : 
  - Suppression des valeurs manquantes et dédoublonnage des fichiers afin d’obtenir des clés primaires uniques avant les jointures entre les données.
  - Jointure des données communes entre ces deux fichiers propres en passant par le fichier intermédiaire liaison.xlsx.
  - Calcul des chiffres d’affaires par bouteille de vins et du chiffre d'affaires total sur les données fusionnées. 
  - Identification des vins premium en appliquant la méthode de z-score sur les prix des vins.

Ton rôle est d’industrialiser ce processus pour que les responsables produits puissent réaliser efficacement leurs ciblages marketing.

Au niveau de l’outil d'automatisation, notre DSI s’est positionné sur Kestra qui semble plus simple à prendre en main.

Nous souhaiterions présenter cette automatisation pour le prochain COPIL. Sur le plan technique, le DSI pourrait donner ses appréciations. Pourrais-tu préparer une présentation pour expliquer à l’ensemble de l’auditoire ta démarche et nous faire une démonstration ? L’objectif est de vulgariser la partie technique d’automatisation. 

Voici les éléments qui nous intéressent : 
  - L’architecture de l’automatisation avec les procédures de tests. C'est-à-dire une conceptualisation des enchaînements des tâches de data transformation réalisées par Stéphane (nettoyages, jointures, agrégations, extractions) avec à l’issue de chaque tâche, une tâche de test pour vérifier que le résultat est juste.
  - L'implémentation de cette architecture avec les tests sur Kestra.
  - Une extraction du rapport au format Excel avec : 
  	- les chiffres d'affaires par produit ;
  -	le chiffre d'affaires total. 
  - Une extraction : 
  	- des vins premium ;
  	- des vins ordinaires.
  - Une planification de l'exécution de l’ensemble du workflow tous les 15 du mois à 9h.
  - Une solution si éventuellement il y avait des dysfonctionnements dans l’automatisation (indisponibilité d’un service tiers comme DuckDB par exemple).

N’hésite pas à solliciter Stéphane (sur la partie analyse de données) ou moi-même si tu as des questions.

Laurent

P.J. : 
Exports.zip


*Cette mission est entièrement guidée.*
*Vous pouvez suivre les étapes ci-dessous.*


## Étapes 1 - Concevez l'architecture d'automatisation (Data lineage)
###Prérequis 
  - Avoir identifié l’enchaînement des tâches demandées.
  - Avoir compris les techniques de schématisation via un diagramme (voir Five Features That Help You to Draw Better Diagrams).

### Résultat attendu
  - Diagramme de flux de l’enchaînement des tâches présentant : 
  	- La liste des tâches à effectuer pour répondre aux demandes métier à partir des 3 fichiers (erp.xlsx, liaison.xlsx, web.xlsx). Pour rappel les éléments demandés par les responsables produits sont  : 
  		- L’extraction du rapport au format Excel avec : 
  			- les chiffres d’affaires par produit ; 
  			- le chiffre d'affaires total.
  		- L’extraction : 
  			- des vins premium ;
  			- des vins ordinaires.
  	- Les liaisons entre ces tâches. 

### Recommandations 
Documentez systématiquement votre travail. Une bonne documentation, y compris un journal de bord ou un rapport de progression, peut aider à suivre les étapes franchies, les défis rencontrés, et les solutions trouvées.
Cette étape, à ne pas sous estimer, vous permettra de conceptualiser l’automatisation de la chaîne de transformation de données. 

### Outils 
  - Draw.io

### Points de vigilance 
N’oubliez pas de schématiser les tests que vous allez mettre en place pour vous assurer que les tâches fonctionnent correctement.


## Étapes 2 - Orchestrez les tâches nominales avec Kestra
### Prérequis 
  - Avoir lu le cours Orchestrez vos workflows avec Kestra. 
  - Avoir installé Kestra sur un Docker.
  	- Consultez le kit d'installation sur le site de Kestra si besoin.
  	- Effectuez quelques captures d'écran de votre installation et du bon fonctionnement de l’outil : elles illustreront votre support de présentation lors de la soutenance. 

### Résultats attendus 
  - Le fichier .yaml Kestra qui est en cohérence avec l’architecture du workflow et qui inclut les scripts de traitement de données : 
  	- Script Python d’identification des vins millésimes et vins ordinaires avec le z-score. Pour rappel : 
  		- score = (prix du vin - moyenne prix des vins)/(écart type des prix des vins) 
  		- un vin millésime est défini comme ayant un z-score  > 2
  	- Script SQL de dédoublonnage avec DuckDB
  	- Script SQL de suppression des doublons avec DuckDB
  	- Script SQL de fusion des deux systèmes avec DuckDB
  	- Script SQL de calcul du chiffre d’affaires par produit et chiffre d'affaires global
  - Après exécution du workflow:
  	- Une extraction du rapport avec les chiffres d’affaires par produit en .xls
  	- Une extraction de la liste des vins premium en .csv
  	- Une extraction des vins ordinaires en .csv
  - Une planification de l'exécution de l’ensemble du workflow tous les 15 du mois à 9h en utilisant le mécanisme du trigger et du cron (voir Crontab.guru)

### Recommandations 
  - Documentez systématiquement votre travail. Une bonne documentation, y compris un journal de bord ou un rapport de progression, peut aider à suivre les étapes franchies, les défis rencontrés, et les solutions trouvées.
  - Une utilisation du mécanisme de branches est recommandée pour extraire les vins premium et les vins ordinaires.

### Outils
  - Kestra
  - Installation des dépendances Python (pandas, …)
  - SQL
  - DuckDB
  - Cours Gérez vos données avec DuckDB

### Points de vigilance
  - Kestra est un outil d’orchestration et non pas un outil de traitement de données.
  - Portez attention aux situations : 
  	- où l'on reçoit de nouvelles sources de données ;
  	- où l'une des tâches du workflow est en erreur. 


## Étapes 3 - Implémenter des tâches de testes avec Kestra
### Prérequis 
  - Avoir lu le cours Orchestrez vos workflows avec Kestra.

### Résultats attendus 
  - Intégration des tâches de tests en SQL ou Python dans les tâches nominales :
  	- Les tests d’absence de doublons
  	- Les tests d’absence de valeurs manquantes
  	- Les tests de cohérence des jointures
  	- Les tests de cohérence du chiffre d'affaires
  	- Le test du Z-score sur le prix des vins
  - Enrichissement du fichier yaml d’orchestration Kestra en intégrant ces tâches de tests

### Recommandations 
Documentez systématiquement votre travail. Une bonne documentation, y compris un journal de bord ou un rapport de progression, peut aider à suivre les étapes franchies, les défis rencontrés, et les solutions trouvées.
Ajoutez les tâches de tests aux tâches nominales créées à l’étape 2.

### Outils 
  - Kestra
  - Python
  - SQL
  - DuckDB

### Points de vigilance 
  - Portez attention aux résultats des analyses effectuées par notre Data Analyst, Stéphane : 
  	- Après dédoublonnage du fichier erp :  825 lignes
  	- Après dédoublonnage du fichier liaison :  825 lignes
  	- Après nettoyage du fichier web :  1428 lignes
  	- Après dédoublonnage du fichier web :  714 lignes
  	- Fichier fusionné : 714 lignes
  	- Le chiffre d'affaires total réalisé est de 70 568.60 euros
  	- Nombre de vins millésimes détectés : 30


## Étapes 4 - Concevez le support de présentation de préparez votre soutenance
### Prérequis 
  - Avoir finalisé votre travail

### Résultat attendu 
Un support de présentation rappelant :
  - le contexte de la mission ; 
  - votre démarche technique complète ;
  - la justification de vos choix.
  et incluant : 
  - le logigramme du processus d’automatisation pour ingérer, nettoyer, fusionner, agréger et extraire les données ; 
  - le workflow Kestra (topologie Kestra) ;
  - la prise en main de Kestra (utiliser un langage simple pour s’adapter au niveau de son interlocuteur) ;
  - les tests mis en place.

### Recommandations 
  - Entraînez-vous à effectuer vos démonstrations en 3 minutes.
  - Anticipez les questions techniques sur les choix d'architecture. Soyez capable de justifier toutes vos décisions. 
  - Soyez prêts à discuter des éventuelles améliorations que vous pourriez apporter au projet, aussi bien sur le plan technique que fonctionnel.
  - Soignez la forme avec des slides claires et concises (des visuels, des schémas, logigrammes, etc.).
  - Préparez votre discours afin qu’il soit fluide et naturel (évitez de lire vos notes). Répétez à l’avance.


## Étapes 5 - Vérifiez votre travail et faites le point avec votre mentor
Pour vérifier que vous n’avez rien oublié dans la réalisation de votre mission, téléchargez et complétez la fiche d’autoévaluation.
Parlez-en avec votre mentor durant votre dernière session de mentorat.

Le fichier Exports.zip a été décompréssé dans _projet/sources/.