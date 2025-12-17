# Guide de Démonstration pour Soutenance (3 minutes)

## Préparation avant la démonstration

### Checklist pré-démo

- [ ] Services AWS démarrés (mongodb + mongo-express)
- [ ] URL Mongo Express accessible : http://34.244.220.245:8081
- [ ] Dashboard CloudWatch ouvert dans un onglet
- [ ] Terminal PowerShell prêt dans le dossier projet
- [ ] Fichier de données de test dans S3 (01_raw/)

### Outils nécessaires

1. **Navigateur** : 
   - Onglet 1 : Mongo Express
   - Onglet 2 : CloudWatch Dashboard
   - Onglet 3 : AWS ECS Console

2. **Terminal** : PowerShell dans le dossier projet

3. **Éditeur** : VS Code avec fichiers clés ouverts

---

## Plan de démonstration (3 minutes)

### 🎯 Objectif

Démontrer que le pipeline fonctionne de bout en bout : **source → S3 → ETL → MongoDB → consultation**

---

### Partie 1 : Vue d'ensemble de l'infrastructure (30 secondes)

**Action** : Montrer le dashboard CloudWatch

```
"Voici notre dashboard de monitoring sur AWS CloudWatch.
On voit que :
- MongoDB et Mongo Express sont actifs (2 tâches en cours)
- CPU et RAM sont à des niveaux normaux (< 20%)
- Nous avons 4,950 documents dans notre base MongoDB
- Le bucket S3 contient nos fichiers transformés"
```

**Transition** : "Voyons maintenant comment les données arrivent dans MongoDB."

---

### Partie 2 : Consultation des données dans MongoDB (45 secondes)

**Action 1** : Ouvrir Mongo Express (http://34.244.220.245:8081)

```
"J'accède à Mongo Express, notre interface web pour MongoDB.
Voici la base 'weather_data' et la collection 'measurements'."
```

**Action 2** : Cliquer sur la collection `measurements`

```
"On a 4,950 documents provenant de 6 stations météorologiques :
- 4 stations InfoClimat (Bergues, Hazebrouck, Armentières, Lille-Lesquin)
- 2 stations Weather Underground (Ichtegem, La Madeleine)"
```

**Action 3** : Afficher un document exemple

```
"Chaque document contient :
- Les données météo (température, pression, humidité, vent)
- Des métadonnées de traçabilité :
  * nom_station : pour identifier la localisation
  * source_file : le fichier source
  * processed_at : timestamp du traitement
  * unique_key : clé unique pour éviter les doublons"
```

**Transition** : "Voyons maintenant comment ces données ont été transformées."

---

### Partie 3 : Exécution d'une requête (30 secondes)

**Action** : Dans Mongo Express, onglet "Simple"

```javascript
// Montrer une requête simple
{
  "nom_station": "Lille-Lesquin"
}
```

**Cliquer sur "Find"**

```
"En une fraction de seconde, on récupère toutes les mesures de Lille-Lesquin.
Nos benchmarks montrent un temps de réponse de 0.27 millisecondes par requête indexée.
C'est largement suffisant pour les notebooks Jupyter des Data Scientists."
```

**Action alternative** : Montrer une agrégation

```javascript
// Dans l'onglet "Aggregation"
[
  {
    "$group": {
      "_id": "$nom_station",
      "temp_moyenne": { "$avg": "$temperature" },
      "count": { "$sum": 1 }
    }
  },
  { "$sort": { "temp_moyenne": -1 } }
]
```

```
"Voici les températures moyennes par station, calculées en 4 millisecondes
sur l'ensemble du dataset."
```

**Transition** : "Maintenant, je vais vous montrer le pipeline ETL en action."

---

### Partie 4 : Démonstration du pipeline ETL (45 secondes)

**Action 1** : Ouvrir terminal PowerShell

```powershell
# Lister les fichiers S3 dans 01_raw/
aws s3 ls s3://p8-weather-data/01_raw/
```

```
"Dans notre bucket S3, dossier 01_raw/, on a les fichiers bruts venant d'Airbyte."
```

**Action 2** : Exécuter l'ETL manuellement (si temps)

```powershell
# Exécuter le script ETL
poetry run python ABAI_P8_script_01_clean_data.py
```

```
"Le script ETL :
1. Lit les fichiers JSONL depuis S3
2. Parse le format Airbyte
3. Fusionne les données de toutes les sources
4. Convertit les unités (°F → °C, mph → km/h, etc.)
5. Génère les unique_key avec séquence pour éviter doublons
6. Sauvegarde le résultat transformé dans 02_cleaned/"
```

**Action 3** : Montrer le résultat

```powershell
# Lister les fichiers transformés
aws s3 ls s3://p8-weather-data/02_cleaned/
```

```
"Voici le fichier JSON transformé, prêt à être importé dans MongoDB.
Le service d'import surveille ce dossier toutes les 5 minutes
et importe automatiquement les nouveaux fichiers."
```

**Transition** : "Enfin, voyons les métriques de qualité."

---

### Partie 5 : Qualité et performance (30 secondes)

**Action 1** : Montrer les statistiques de qualité

```
"Nos contrôles qualité montrent :
- 0% d'erreur : 4,950 documents importés sur 4,950
- 0 doublon : grâce à l'index unique sur unique_key
- 100% de conformité des types : températures, pressions, humidité validées

En termes de performance :
- Temps d'écriture : 87,840 documents/seconde
- Temps de lecture indexée : 0.27 milliseconde
- Temps d'agrégation : 4.1 millisecondes

Ces performances dépassent largement les besoins des Data Scientists."
```

**Action 2** : Montrer les services AWS ECS (optionnel si temps)

```
"Sur AWS ECS, on a 5 services :
- MongoDB : base de données (actif)
- Mongo Express : interface web (actif)
- weather-etl : transformation des données (manuel, arrêté pour économiser)
- mongodb-importer : import automatique (manuel, arrêté)
- s3-cleanup : nettoyage S3 (manuel, arrêté)

Les services manuels ne coûtent rien quand ils sont arrêtés.
Infrastructure totale : ~1$/jour pour MongoDB + Mongo Express."
```

---

### Conclusion (10 secondes - optionnel)

```
"En résumé :
- Pipeline complètement fonctionnel de bout en bout
- Données de qualité (0% d'erreur)
- Performances excellentes (< 1 ms)
- Infrastructure AWS scalable et économique

Le système est prêt pour production et peut gérer 100x plus de données
sans modification majeure."
```

---

## Scénarios de secours

### Si Mongo Express ne répond pas

**Plan B** : Utiliser MongoDB Shell via ECS Exec

```powershell
# Se connecter au conteneur MongoDB
$taskArn = (aws ecs list-tasks --cluster weather-pipeline-cluster --service-name mongodb --region eu-west-1 --query 'taskArns[0]' --output text)
aws ecs execute-command --cluster weather-pipeline-cluster --task $taskArn --container mongodb --command "mongosh" --interactive --region eu-west-1
```

```javascript
// Dans mongosh
use weather_data
db.measurements.countDocuments()
db.measurements.findOne()
```

---

### Si services AWS sont arrêtés

**Plan B** : Démonstration avec environnement local

```powershell
# Démarrer docker-compose local
cd local
docker-compose up -d

# Attendre 30 secondes
Start-Sleep -Seconds 30

# Accéder à Mongo Express local
# http://localhost:8081
```

---

### Si pas de temps pour exécution ETL

**Plan B** : Montrer les logs CloudWatch

```
"Voici les logs d'une exécution précédente du script ETL.
On voit :
- Lecture de 3 fichiers JSONL depuis S3
- Détection de 6 stations
- Fusion de 4,950 enregistrements
- Temps d'exécution total : 3.2 secondes"
```

---

## Tableau de bord des URLs

| Ressource | URL | Login | Notes |
|-----------|-----|-------|-------|
| **Mongo Express** | http://34.244.220.245:8081 | admin/pass | Interface web MongoDB |
| **CloudWatch Dashboard** | [Lien Console AWS](https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=eu-west-1#dashboards/dashboard/weather-pipeline-monitoring) | AWS Console | Métriques temps réel |
| **ECS Console** | [Lien ECS](https://eu-west-1.console.aws.amazon.com/ecs/v2/clusters/weather-pipeline-cluster/services) | AWS Console | Statut services |
| **S3 Bucket** | s3://p8-weather-data | AWS CLI | Fichiers bruts/transformés |

---

## Points clés à mentionner

### Pour Ouly (Data Scientist lead)

1. **Schéma flexible** : "Vous pouvez requêter MongoDB comme du JSON, pas besoin de connaître SQL"
2. **Performance** : "Temps de réponse < 1 ms, vous ne verrez aucune latence dans vos notebooks"
3. **Traçabilité** : "Chaque mesure garde le nom du fichier source, vous pouvez retracer l'origine"
4. **Fiabilité** : "0% d'erreur, unique_key garantit pas de doublons dans vos modèles"

### Pour l'évaluateur technique

1. **Architecture** : "Microservices dockerisés sur ECS Fargate, hautement scalable"
2. **Qualité** : "Suite de tests automatisés (pytest) + validation schéma MongoDB"
3. **Monitoring** : "CloudWatch Dashboard + Benchmark de performance intégrés"
4. **Coût** : "Infrastructure optimisée : ~1$/jour, services manuels arrêtables pour économiser"

---

## Timing détaillé (3 minutes)

| Partie | Durée | Timing cumulé |
|--------|-------|---------------|
| 1. Dashboard CloudWatch | 30s | 0:30 |
| 2. Mongo Express + Requête | 45s | 1:15 |
| 3. Pipeline ETL | 45s | 2:00 |
| 4. Qualité/Performance | 30s | 2:30 |
| 5. Conclusion | 10s | 2:40 |
| **Buffer** | 20s | **3:00** |

**Note** : Prévoir 20 secondes de buffer pour questions/imprévus

---

## Commandes à préparer dans le terminal

### Terminal 1 : AWS S3

```powershell
# Lister fichiers raw
aws s3 ls s3://p8-weather-data/01_raw/

# Lister fichiers cleaned
aws s3 ls s3://p8-weather-data/02_cleaned/

# Lister fichiers archived
aws s3 ls s3://p8-weather-data/03_archived/
```

### Terminal 2 : Statut services

```powershell
# Statut des services ECS
aws ecs describe-services --cluster weather-pipeline-cluster --services mongodb mongo-express --region eu-west-1 --query 'services[].{Service:serviceName,Status:status,Desired:desiredCount,Running:runningCount}' --output table
```

### Terminal 3 : Exécution scripts (optionnel)

```powershell
# ETL
poetry run python ABAI_P8_script_01_clean_data.py

# Benchmark
poetry run python ABAI_P8_script_05_benchmark_mongodb.py
```

---

## Checklist post-démonstration

- [ ] Tous les services arrêtés ? (sauf mongodb + mongo-express si présentation continue)
- [ ] Vérifier facturation AWS (billing dashboard)
- [ ] Sauvegarder logs CloudWatch si nécessaire
- [ ] Commit/push dernières modifications Git

---

## Questions anticipées

### "Combien de temps pour ajouter une nouvelle source de données ?"

**Réponse** : 
"5-10 minutes avec Airbyte. On ajoute un nouveau connecteur source, 
on configure la destination S3, et le pipeline ETL détecte automatiquement 
le nouveau format et fusionne les données. Aucune modification de code nécessaire."

### "Quelle est la capacité maximale du système ?"

**Réponse** :
"Actuellement 4,950 documents, mais l'architecture peut gérer 100x plus (500k docs) 
sans modification. Au-delà, on passerait à MongoDB Replica Set avec sharding horizontal. 
ECS Fargate peut auto-scale de 1 à 100+ tâches selon la charge."

### "Comment gérez-vous les pannes ?"

**Réponse** :
"Plusieurs niveaux de résilience :
1. ECS redémarre automatiquement les tâches qui échouent
2. EFS réplique les données sur plusieurs AZ (Multi-AZ)
3. S3 garde l'historique (03_archived/) pour retraitement si besoin
4. Tests pre-import détectent les problèmes avant d'écrire dans MongoDB"

### "Coût mensuel ?"

**Réponse** :
"Configuration actuelle : ~30-35$/mois
- MongoDB + Mongo Express : ~1$/jour = 30$/mois
- EFS : ~1.50$/mois (5 GB)
- S3 : < 0.10$/mois (3 MB)
- CloudWatch : ~0.50$/mois

Services ETL/Import/Cleanup sont arrêtables quand pas utilisés (0$ si arrêtés)."

---

## Bonnes pratiques de présentation

### ✅ À faire

- **Répéter** : S'entraîner 3-4 fois avant la soutenance
- **Chronométrer** : Respecter les 3 minutes (utiliser chronomètre)
- **Tester** : Vérifier tous les services 30 min avant la soutenance
- **Préparer backup** : Plan B si problème réseau/AWS
- **Parler clairement** : Pas de jargon inutile, expliquer les acronymes

### ❌ À éviter

- **Lire ses notes** : Parler naturellement, pas de lecture
- **Trop de détails** : Rester haut niveau, approfondir si questions
- **Silence** : Commenter en continu ce qu'on fait à l'écran
- **Improviser** : Tout doit être préparé et testé
- **Dépasser le temps** : Couper si nécessaire, aller à la conclusion

---

## Résumé : Les 3 minutes en mode express

Si pressé par le temps, version ultra-condensée :

1. **CloudWatch Dashboard** (20s) : "Infrastructure opérationnelle, 4,950 documents"
2. **Mongo Express** (40s) : "Requête en 0.27ms, données de 6 stations"
3. **Terminal S3 + ETL** (40s) : "Pipeline automatique S3 → ETL → MongoDB"
4. **Qualité** (20s) : "0% erreur, performances excellentes"
5. **Conclusion** (10s) : "Système prêt pour production"

**Total : 2:10** (50s de buffer pour questions)
